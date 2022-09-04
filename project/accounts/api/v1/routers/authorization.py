from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import true

from accounts.api.v1.schemas import authentication as authorization_schemas
from accounts.api.v1.schemas import users as user_schemas
from accounts.models import User
from accounts.services.authorization import ConfirmationTokensCreateServiceABC, ConfirmationTokensConfirmServiceABC
from accounts.services.exceptions.authorization import InvalidConfirmationTokenException
from accounts.services.users import UsersCreateUpdateServiceABC, UsersRetrieveServiceABC
from core.authentication.services.jwt_authentication import JWTAuthenticationServiceABC
from core.config import settings
from notifications.async_tasks.email import send_email

router = APIRouter()


@router.post('/registration')
async def registration_view(
        user_data: user_schemas.UserCreateSchema,
        users_create_update_service: UsersCreateUpdateServiceABC = Depends(),
        confirmation_tokens_create_service: ConfirmationTokensCreateServiceABC = Depends(),
) -> str:
    user_data = user_data.dict()
    user_data['is_active'] = False
    nickname = user_data.pop('nickname')
    email = user_data.pop('email')
    password = user_data.pop('password')
    # TODO: create a separate service for proper creation of user and token and sending an email in the end
    user = await users_create_update_service.create_user(nickname, email, password, **user_data)
    token = await confirmation_tokens_create_service.create_confirmation_token(user)
    email_data = {'link': f'{settings.HOST_DOMAIN}/accounts/confirm_email?token={token.token}'}
    await send_email('email_confirmation.html', 'Please confirm your email', email, template_body=email_data)
    return 'Registration is successful, confirm your email.'


@router.post('/confirm_token')
async def confirm_token_view(
        token_data: authorization_schemas.TokenConfirmationSchema,
        request_user: User = Depends(),
        confirmation_tokens_confirm_service: ConfirmationTokensConfirmServiceABC = Depends(),
) -> str:
    try:
        await confirmation_tokens_confirm_service.confirm_confirmation_token(request_user, token_data.token)
    except InvalidConfirmationTokenException as e:
        raise HTTPException(status_code=404, detail=str(e))
    return 'Token is successfully confirmed.'


@router.post('/login')
async def login_view(
        login_data: authorization_schemas.LoginSchema,
        users_retrieve_service: UsersRetrieveServiceABC = Depends(),
        jwt_authentication_service: JWTAuthenticationServiceABC = Depends(),
) -> dict[str, str]:
    user = await users_retrieve_service.get_one_user(User.email == login_data.email, User.is_active == true())
    if user and user.check_password(login_data.password):
        user_id = user.id
        access_token = await jwt_authentication_service.create_token(user_id, settings.JWT_ACCESS_TOKEN_TYPE)
        refresh_token = await jwt_authentication_service.create_token(user_id, settings.JWT_REFRESH_TOKEN_TYPE)
        return {'access_token': access_token, 'refresh_token': refresh_token}
    raise HTTPException(status_code=400, detail='Invalid email or password')


@router.post('/refresh_token')
async def refresh_token_view(
        token_data: authorization_schemas.RefreshTokenSchema,
        jwt_authentication_service: JWTAuthenticationServiceABC = Depends(),
) -> dict[str, str]:
    user = await jwt_authentication_service.validate_token(token_data.refresh_token, [settings.JWT_REFRESH_TOKEN_TYPE])
    if user:
        access_token = await jwt_authentication_service.create_token(user.id, settings.JWT_ACCESS_TOKEN_TYPE)
        return {'access_token': access_token}
    raise HTTPException(status_code=400, detail='Invalid refresh token')

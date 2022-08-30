from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy import select, true
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.api.v1.schemas import authentication as authorization_schemas
from accounts.api.v1.schemas import users as user_schemas
from accounts.models import User, EmailConfirmationToken
from accounts.services.authorization import ConfirmationTokensServiceABC
from accounts.services.users import UsersCreateUpdateServiceABC, UsersRetrieveServiceABC
from core.authentication.services.jwt_authentication import JWTAuthenticationServiceABC
from core.config import settings
from notifications.background_tasks.email import send_email

router = APIRouter()


@router.post('/registration')
async def registration_view(
        user: user_schemas.UserCreateSchema,
        background_tasks: BackgroundTasks,
        users_create_update_service: UsersCreateUpdateServiceABC = Depends(),
        confirmation_token_service: ConfirmationTokensServiceABC = Depends(),
) -> str:
    user_data = user.dict()
    user_data['is_active'] = False
    nickname = user_data.pop('nickname')
    email = user_data.pop('email')
    password = user_data.pop('password')
    user = await users_create_update_service.create_user(nickname, email, password, **user_data)
    token = await confirmation_token_service.create_confirmation_token(user)
    email_data = {'link': f'{settings.HOST_DOMAIN}/accounts/confirm_email?token={token.token}'}
    send_email(
        background_tasks, 'email_confirmation.html', 'Please confirm your email', user.email, template_body=email_data,
    )
    return 'Registration is successful, confirm your email.'


@router.post('/confirm_email')
async def confirm_email_view(
        token: authorization_schemas.EmailConfirmationSchema,
        users_retrieve_service: UsersRetrieveServiceABC = Depends(),
        users_create_update_service: UsersCreateUpdateServiceABC = Depends(),
) -> str:
    get_user_query = select(User).join(
        User.email_confirmation_tokens,
    ).where(
        EmailConfirmationToken.created_at >= datetime.now() - timedelta(settings.EMAIL_CONFIRMATION_TOKEN_VALID_HOURS),
        EmailConfirmationToken.token == token.token,
    )
    user = await users_retrieve_service.get_one_user(db_query=get_user_query)
    await users_create_update_service.update_user(user, is_active=True)
    return 'Your email is successfully confirmed.'


@router.post('/login')
async def login_view(
        login_data: authorization_schemas.LoginSchema,
        db_session: AsyncSession = Depends(),
        jwt_authentication_service: JWTAuthenticationServiceABC = Depends(),
) -> dict[str, str]:
    get_user_query = select(User).where(User.email == login_data.email, User.is_active == true())
    user = await db_session.scalar(get_user_query)
    if user and user.check_password(login_data.password):
        user_id = user.id
        access_token = await jwt_authentication_service.create_token(user_id, settings.JWT_ACCESS_TOKEN_TYPE)
        refresh_token = await jwt_authentication_service.create_token(user_id, settings.JWT_REFRESH_TOKEN_TYPE)
        return {'access_token': access_token, 'refresh_token': refresh_token}
    raise HTTPException(status_code=400, detail='Invalid email or password')


@router.post('/refresh_token')
async def refresh_token_view(
        token: authorization_schemas.RefreshTokenSchema,
        jwt_authentication_service: JWTAuthenticationServiceABC = Depends(),
) -> dict[str, str]:
    user = await jwt_authentication_service.validate_token(token.refresh_token, [settings.JWT_REFRESH_TOKEN_TYPE])
    if user:
        access_token = await jwt_authentication_service.create_token(user.id, settings.JWT_ACCESS_TOKEN_TYPE)
        return {'access_token': access_token}
    raise HTTPException(status_code=400, detail='Invalid refresh token')

from accounts.api.v1.schemas import authentication as authorization_schemas
from accounts.api.v1.schemas import users as user_schemas
from accounts.models import User
from accounts.services.authentication.authentication import ConfirmationTokensConfirmServiceABC
from accounts.services.authentication.jwt_authentication import JWTAuthenticationServiceABC
from accounts.services.authentication.registration import UsersRegistrationServiceABC
from accounts.services.exceptions.authentication import (
    ConfirmationTokenCreationException,
    InvalidConfirmationTokenException,
)
from accounts.services.exceptions.users import UserCreationException
from accounts.services.users import UsersRetrieveServiceABC
from core.config import SettingsABC
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import true

router = APIRouter()


@router.post('/registration')
async def registration_view(
    user_data: user_schemas.UserCreateSchema,
    users_registration_service: UsersRegistrationServiceABC = Depends(),
) -> str:
    user_data = user_data.dict()
    nickname = user_data.pop('nickname')
    email = user_data.pop('email')
    password = user_data.pop('password')
    try:
        await users_registration_service.registrate_user(nickname, email, password, **user_data)
    except (UserCreationException, ConfirmationTokenCreationException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return 'Registration is successful, confirm your email.'


@router.post('/confirm_token')
async def confirm_token_view(
    token_data: authorization_schemas.TokenConfirmationSchema,
    confirmation_tokens_confirm_service: ConfirmationTokensConfirmServiceABC = Depends(),
    settings: SettingsABC = Depends(),
    jwt_authentication_service: JWTAuthenticationServiceABC = Depends(),
) -> dict[str, str]:
    try:
        user = await confirmation_tokens_confirm_service.confirm_confirmation_token(
            token_data.user_id,
            token_data.token,
        )
    except InvalidConfirmationTokenException as e:
        raise HTTPException(status_code=404, detail=str(e))
    access_token = await jwt_authentication_service.create_token(user.id, settings.JWT_ACCESS_TOKEN_TYPE)
    refresh_token = await jwt_authentication_service.create_token(user.id, settings.JWT_REFRESH_TOKEN_TYPE)
    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.post('/login')
async def login_view(
    login_data: authorization_schemas.LoginSchema,
    settings: SettingsABC = Depends(),
    users_retrieve_service: UsersRetrieveServiceABC = Depends(),
    jwt_authentication_service: JWTAuthenticationServiceABC = Depends(),
) -> dict[str, str]:
    user = await users_retrieve_service.get_one_user(User.email == login_data.email, User.is_active == true())
    if user and user.check_password(login_data.password):
        access_token = await jwt_authentication_service.create_token(user.id, settings.JWT_ACCESS_TOKEN_TYPE)
        refresh_token = await jwt_authentication_service.create_token(user.id, settings.JWT_REFRESH_TOKEN_TYPE)
        return {'access_token': access_token, 'refresh_token': refresh_token}
    raise HTTPException(status_code=400, detail='Invalid email or password')


@router.post('/refresh_token')
async def refresh_token_view(
    token_data: authorization_schemas.RefreshTokenSchema,
    settings: SettingsABC = Depends(),
    jwt_authentication_service: JWTAuthenticationServiceABC = Depends(),
) -> dict[str, str]:
    user = await jwt_authentication_service.validate_token(token_data.refresh_token, [settings.JWT_REFRESH_TOKEN_TYPE])
    if user:
        access_token = await jwt_authentication_service.create_token(user.id, settings.JWT_ACCESS_TOKEN_TYPE)
        return {'access_token': access_token}
    raise HTTPException(status_code=400, detail='Invalid refresh token')

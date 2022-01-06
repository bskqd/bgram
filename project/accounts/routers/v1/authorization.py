from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy import select, true
from sqlalchemy.orm import Session

from accounts.crud import users as user_crud
from accounts.models import User, EmailConfirmationToken
from accounts.schemas import users as user_schemas, authorization as authorization_schemas
from accounts.services import authorization as authorization_services
from core.config import settings
from core.services.authorization import JWTAuthenticationServices
from mixins import dependencies as mixins_dependencies
from mixins.services import crud as mixins_crud_services
from notifications.background_tasks.email import send_email

router = APIRouter()


@router.post('/registration')
async def registration_view(
        user: user_schemas.UserCreateSchema,
        background_tasks: BackgroundTasks,
        db_session: Session = Depends(mixins_dependencies.db_session),
) -> str:
    user_data = user.dict()
    user_data['is_active'] = False
    nickname = user_data.pop('nickname')
    email = user_data.pop('email')
    password = user_data.pop('password')
    user = await user_crud.create_user(nickname, email, password, db_session, **user_data)
    token = await authorization_services.create_email_confirmation_token(user, db_session)
    email_data = {'link': f'{settings.HOST_DOMAIN}/accounts/confirm_email?token={token.token}'}
    send_email(
        background_tasks, 'email_confirmation.html', 'Please confirm your email', user.email, template_body=email_data
    )
    return 'Registration is successful, confirm your email.'


@router.post('/login')
async def login_view(
        login_data: authorization_schemas.LoginSchema,
        db_session: Session = Depends(mixins_dependencies.db_session)
) -> dict[str, str]:
    get_user_query = select(User).where(User.email == login_data.email, User.is_active == true())
    user = await db_session.execute(get_user_query)
    user = user.scalar()
    if user and user.check_password(login_data.password):
        user_id = user.id
        access_token = await JWTAuthenticationServices.create_token(user_id, settings.JWT_ACCESS_TOKEN_TYPE)
        refresh_token = await JWTAuthenticationServices.create_token(user_id, settings.JWT_REFRESH_TOKEN_TYPE)
        return {'access_token': access_token, 'refresh_token': refresh_token}
    raise HTTPException(status_code=400, detail='Invalid email or password')


@router.post('/confirm_email')
async def confirm_email_view(
        token: authorization_schemas.EmailConfirmationSchema,
        db_session: Session = Depends(mixins_dependencies.db_session)
) -> str:
    get_user_query = select(User).join(
        User.email_confirmation_tokens
    ).where(
        EmailConfirmationToken.created_at >= datetime.now() - timedelta(settings.EMAIL_CONFIRMATION_TOKEN_VALID_HOURS)
    )
    user = await mixins_crud_services.CRUDOperationsService(db_session).get_object(
        get_user_query, EmailConfirmationToken, token.token, 'token'
    )
    await user_crud.update_user(user, db_session, is_active=True)
    return 'Your email is successfully confirmed.'


@router.post('/refresh_token')
async def refresh_token_view(token: authorization_schemas.RefreshTokenSchema) -> dict[str, str]:
    user = await JWTAuthenticationServices.validate_token(token.refresh_token, [settings.JWT_REFRESH_TOKEN_TYPE])
    if user:
        access_token = await JWTAuthenticationServices.create_token(user.id, settings.JWT_ACCESS_TOKEN_TYPE)
        return {'access_token': access_token}
    raise HTTPException(status_code=400, detail='Invalid refresh token')

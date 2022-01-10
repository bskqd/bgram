from typing import List

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from accounts.models import User, UserPhoto
from accounts.utils.users import get_hashed_password
from mixins.services import crud as mixins_crud_services, files as mixins_files_services


async def create_user(nickname: str, email: str, password: str, db_session: Session, **kwargs) -> User:
    user = User(nickname=nickname, email=email, password=get_hashed_password(password), **kwargs)
    await mixins_crud_services.CRUDOperationsService(db_session).create_object_in_database(user)
    return user


async def get_users(db_session: Session, queryset: Select = select(User)) -> List[User]:
    users = await db_session.execute(queryset)
    return users.unique().scalars().all()


async def get_user(
        search_value: int,
        db_session: Session,
        lookup_kwarg: str = 'id',
        queryset: Select = select(User)
) -> User:
    return await mixins_crud_services.CRUDOperationsService(db_session).get_object(
        queryset, User, search_value, lookup_kwarg=lookup_kwarg
    )


async def update_user(user: User, db_session: Session, **data_for_update) -> User:
    return await mixins_crud_services.CRUDOperationsService(db_session).update_object_in_database(
        user, **data_for_update
    )


async def create_user_photo(user_id: int, file: UploadFile, db_session: Session) -> UserPhoto:
    return await mixins_files_services.FilesService(db_session).create_object_file(UserPhoto, file, user_id=user_id)

from fastapi import UploadFile

from accounts.models import User, UserPhoto
from accounts.utils.users import get_hashed_password
from database.repository import SQLAlchemyCRUDRepository
from mixins.services import files as mixins_files_services


class UserService:
    def __init__(self, db_repository: SQLAlchemyCRUDRepository):
        self.db_repository = db_repository

    async def create_user(self, nickname: str, email: str, password: str, **kwargs) -> User:
        user = User(nickname=nickname, email=email, password=get_hashed_password(password), **kwargs)
        await self.db_repository.create(user)
        await self.db_repository.commit()
        await self.db_repository.refresh(user)
        return user

    async def update_user(self, user: User, **data_for_update) -> User:
        user = await self.db_repository.update_object(user, **data_for_update)
        await self.db_repository.commit()
        await self.db_repository.refresh(user)
        return user

    async def create_user_photo(self, user_id: int, file: UploadFile) -> UserPhoto:
        return await mixins_files_services.FilesService(self.db_repository).create_object_file(
            UserPhoto, file, user_id=user_id
        )

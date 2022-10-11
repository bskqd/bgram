from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.api.filters.users import UsersFilterSet, UserFilterSetABC
from accounts.api.pagination.users import UsersPaginationDatabaseObjectsRetrieverStrategy, UsersPaginatorABC
from accounts.database.repository.users import UsersDatabaseRepositoryABC, UserFilesDatabaseRepositoryABC
from accounts.models import User, UserFile
from accounts.services.users import (
    UsersRetrieveService, UsersCreateUpdateService, UsersRetrieveServiceABC, UserFilesService,
    UsersCreateUpdateServiceABC, UserFilesServiceABC,
)
from core.config import SettingsABC
from core.database.repository import SQLAlchemyDatabaseRepository
from core.filters import FilterSet
from core.pagination import DefaultPaginationClass


class UsersDependenciesOverrides:
    @classmethod
    def override_dependencies(cls) -> dict:
        return {
            UsersDatabaseRepositoryABC: cls.get_users_db_repository,
            UserFilesDatabaseRepositoryABC: cls.get_user_files_db_repository,
            UsersRetrieveServiceABC: cls.get_users_retrieve_service,
            UsersCreateUpdateServiceABC: cls.get_users_create_update_service,
            UsersPaginatorABC: cls.get_users_paginator,
            UserFilterSetABC: cls.get_users_filterset,
            UserFilesServiceABC: cls.get_user_files_service,
        }

    @staticmethod
    async def get_users_db_repository(db_session: AsyncSession = Depends()):
        return SQLAlchemyDatabaseRepository(User, db_session)

    @staticmethod
    async def get_user_files_db_repository(db_session: AsyncSession = Depends()):
        return SQLAlchemyDatabaseRepository(UserFile, db_session)

    @staticmethod
    async def get_users_retrieve_service(db_repository: UsersDatabaseRepositoryABC = Depends()):
        return UsersRetrieveService(db_repository)

    @staticmethod
    async def get_users_create_update_service(
            db_repository: UsersDatabaseRepositoryABC = Depends(),
            settings: SettingsABC = Depends(),
    ):
        return UsersCreateUpdateService(db_repository, settings)

    @staticmethod
    async def get_user_files_service(db_repository: UserFilesDatabaseRepositoryABC = Depends()):
        return UserFilesService(db_repository)

    @staticmethod
    async def get_users_filterset(request: Request) -> FilterSet:
        return UsersFilterSet(request=request)

    @staticmethod
    async def get_users_paginator(
            request: Request,
            users_retrieve_service: UsersRetrieveServiceABC = Depends(),
    ) -> DefaultPaginationClass:
        users_db_objects_retriever_strategy = UsersPaginationDatabaseObjectsRetrieverStrategy(users_retrieve_service)
        return DefaultPaginationClass(request, users_db_objects_retriever_strategy)

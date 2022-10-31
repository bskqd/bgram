from accounts.api.filters.users import UserFilterSetABC, UsersFilterSet
from accounts.api.pagination.users import UsersPaginationDatabaseObjectsRetrieverStrategy, UsersPaginatorABC
from accounts.database.repository.users import UserFilesDatabaseRepositoryABC, UsersDatabaseRepositoryABC
from accounts.dependencies.users.providers import (
    provide_user_files_db_repository,
    provide_user_files_service,
    provide_users_create_update_service,
    provide_users_db_repository,
    provide_users_retrieve_service,
)
from accounts.services.users import UserFilesServiceABC, UsersCreateUpdateServiceABC, UsersRetrieveServiceABC
from core.config import SettingsABC
from core.filters import FilterSet
from core.pagination import DefaultPaginationClass
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


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
    async def get_users_db_repository(db_session: AsyncSession = Depends()) -> UsersDatabaseRepositoryABC:
        return provide_users_db_repository(db_session)

    @staticmethod
    async def get_user_files_db_repository(db_session: AsyncSession = Depends()) -> UserFilesDatabaseRepositoryABC:
        return provide_user_files_db_repository(db_session)

    @staticmethod
    async def get_users_retrieve_service(
        db_repository: UsersDatabaseRepositoryABC = Depends(),
    ) -> UsersRetrieveServiceABC:
        return provide_users_retrieve_service(db_repository)

    @staticmethod
    async def get_users_create_update_service(
        db_repository: UsersDatabaseRepositoryABC = Depends(),
        settings: SettingsABC = Depends(),
    ) -> UsersCreateUpdateServiceABC:
        return provide_users_create_update_service(db_repository, settings)

    @staticmethod
    async def get_user_files_service(db_repository: UserFilesDatabaseRepositoryABC = Depends()) -> UserFilesServiceABC:
        return provide_user_files_service(db_repository)

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

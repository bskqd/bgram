from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.api.filters.users import UsersFilterSet
from accounts.api.pagination.users import UsersPaginationDatabaseObjectsRetrieverStrategy
from accounts.models import User, UserPhoto
from accounts.services.users import UsersRetrieveService, UsersCreateUpdateService
from core.database.repository import SQLAlchemyCRUDRepository, BaseCRUDRepository
from core.filters import FilterSet
from core.pagination import DefaultPaginationClass
from core.services.files import FilesService


async def get_users_db_repository(db_session: AsyncSession = Depends()) -> BaseCRUDRepository:
    return SQLAlchemyCRUDRepository(User, db_session)


async def get_users_retrieve_service(db_repository=Depends(get_users_db_repository)):
    return UsersRetrieveService(db_repository)


async def get_users_create_update_service(db_repository=Depends(get_users_db_repository)):
    return UsersCreateUpdateService(db_repository)


async def get_user_photos_service(db_repository=Depends(get_users_db_repository)):
    return FilesService(db_repository, UserPhoto)


async def get_users_filterset(request: Request) -> FilterSet:
    return UsersFilterSet(request=request)


async def get_users_paginator(
        request: Request,
        users_retrieve_service=Depends(get_users_retrieve_service)
) -> DefaultPaginationClass:
    users_db_objects_retriever_strategy = UsersPaginationDatabaseObjectsRetrieverStrategy(users_retrieve_service)
    return DefaultPaginationClass(request, users_db_objects_retriever_strategy)

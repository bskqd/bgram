from fastapi import APIRouter, UploadFile, File, Depends

from accounts.api.filters.users import IUserFilterSet
from accounts.api.pagination.users import IUsersPaginator
from accounts.api.v1.schemas import users as user_schemas
from accounts.api.v1.schemas.users import PaginatedUsersListSchema
from accounts.api.v1.selectors.users import get_users_db_query
from accounts.models import User
from accounts.services.users import IUsersRetrieveService, IUsersCreateUpdateService, UserPhotoService

router = APIRouter()


@router.get('/users', response_model=PaginatedUsersListSchema)
async def list_users_view(
        request_user: User = Depends(),
        users_filterset: IUserFilterSet = Depends(),
        users_paginator: IUsersPaginator = Depends(),
):
    return await users_paginator.paginate(users_filterset.filter_db_query(db_query=get_users_db_query(request_user)))


@router.get('/users/{user_id}', response_model=user_schemas.UsersListSchema)
async def retrieve_user_view(
        user_id: int,
        request_user: User = Depends(),
        users_retrieve_service: IUsersRetrieveService = Depends(),
):
    return await users_retrieve_service.get_one_user(User.id == user_id, db_query=get_users_db_query(request_user))


@router.patch('/users/{user_id}', response_model=user_schemas.UsersListSchema)
async def update_user_view(
        user_id: int,
        user_data: user_schemas.UserUpdateSchema,
        request_user: User = Depends(),
        users_retrieve_service: IUsersRetrieveService = Depends(),
        users_update_service: IUsersCreateUpdateService = Depends(),
):
    user = await users_retrieve_service.get_one_user(User.id == user_id, db_query=get_users_db_query(request_user))
    return await users_update_service.update_user(user, **user_data.dict(exclude_unset=True))


@router.post('/users/{user_id}/upload_file', response_model=user_schemas.UsersListSchema)
async def upload_user_photo_view(
        user_id: int,
        file: UploadFile = File(...),
        request_user: User = Depends(),
        user_photos_service: UserPhotoService = Depends(),
        users_retrieve_service: IUsersRetrieveService = Depends(),
):
    await user_photos_service.create_object_file(file, user_id=user_id)
    return await users_retrieve_service.get_one_user(User.id == user_id, db_query=get_users_db_query(request_user))

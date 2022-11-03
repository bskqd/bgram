from accounts.api.filters.users import UserFilterSetABC
from accounts.api.pagination.users import UsersPaginatorABC
from accounts.api.v1.schemas import users as user_schemas
from accounts.api.v1.schemas.users import PaginatedUsersListSchema
from accounts.database.selectors.users import get_user_update_returning_options, get_users_db_query
from accounts.models import User
from accounts.services.users import UserFilesServiceABC, UsersCreateUpdateServiceABC, UsersRetrieveServiceABC
from fastapi import APIRouter, Depends, File, UploadFile

router = APIRouter()


@router.get('/users', response_model=PaginatedUsersListSchema)
async def list_users_view(
    request_user: User = Depends(),
    users_filterset: UserFilterSetABC = Depends(),
    users_paginator: UsersPaginatorABC = Depends(),
):
    return await users_paginator.paginate(users_filterset.filter_db_query(db_query=get_users_db_query(request_user)))


@router.get('/users/{user_id}', response_model=user_schemas.UsersListSchema)
async def retrieve_user_view(
    user_id: int,
    request_user: User = Depends(),
    users_retrieve_service: UsersRetrieveServiceABC = Depends(),
):
    return await users_retrieve_service.get_one_user(User.id == user_id, db_query=get_users_db_query(request_user))


@router.patch('/users/{user_id}', response_model=user_schemas.UsersListSchema)
async def update_user_view(
    user_id: int,
    user_data: user_schemas.UserUpdateSchema,
    users_update_service: UsersCreateUpdateServiceABC = Depends(),
):
    return await users_update_service.update_user(
        user_id,
        _returning_options=get_user_update_returning_options(),
        **user_data.dict(exclude_unset=True),
    )


@router.post('/users/{user_id}/upload_file', response_model=user_schemas.UsersListSchema)
async def upload_user_photo_view(
    user_id: int,
    file: UploadFile = File(...),
    request_user: User = Depends(),
    user_files_service: UserFilesServiceABC = Depends(),
    users_retrieve_service: UsersRetrieveServiceABC = Depends(),
):
    await user_files_service.create_object_file(file, user_id=user_id)
    return await users_retrieve_service.get_one_user(User.id == user_id, db_query=get_users_db_query(request_user))

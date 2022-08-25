import asyncio
from datetime import timedelta

from apscheduler.triggers.date import DateTrigger, datetime
from fastapi import APIRouter, UploadFile, File, Depends
from pytz import utc

from accounts.api.filters.users import UserFilterSetABC
from accounts.api.pagination.users import UsersPaginatorABC
from accounts.api.v1.schemas import users as user_schemas
from accounts.api.v1.schemas.users import PaginatedUsersListSchema
from accounts.api.v1.selectors.users import get_users_db_query
from accounts.models import User
from accounts.services.users import UsersRetrieveServiceABC, UsersCreateUpdateServiceABC, UserFilesServiceABC
from core.dependencies import Scheduler
from core.scheduler import celery_task

router = APIRouter()


@router.get('/test_beat')
async def test_beat(scheduler: Scheduler = Depends()):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        scheduler.add_job,
        celery_task,
        DateTrigger(
            run_date=datetime.now() - timedelta(hours=3),
            timezone=utc,
        ),
        None,
        None,
        None,
        'core.celery.celery_app.test',
    )
    return ''


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
        request_user: User = Depends(),
        users_retrieve_service: UsersRetrieveServiceABC = Depends(),
        users_update_service: UsersCreateUpdateServiceABC = Depends(),
):
    user = await users_retrieve_service.get_one_user(User.id == user_id, db_query=get_users_db_query(request_user))
    return await users_update_service.update_user(user, **user_data.dict(exclude_unset=True))


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

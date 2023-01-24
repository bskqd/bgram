from accounts.database.repository.users import (
    UserFilesDatabaseRepository,
    UserFilesDatabaseRepositoryABC,
    UsersDatabaseRepository,
    UsersDatabaseRepositoryABC,
)
from accounts.services.users import (
    UserFilesService,
    UserFilesServiceABC,
    UsersCreateUpdateService,
    UsersCreateUpdateServiceABC,
    UsersDeleteService,
    UsersDeleteServiceABC,
    UsersRetrieveService,
    UsersRetrieveServiceABC,
)
from core.config import SettingsABC
from sqlalchemy.ext.asyncio import AsyncSession


def provide_users_db_repository(db_session: AsyncSession) -> UsersDatabaseRepositoryABC:
    return UsersDatabaseRepository(db_session)


def provide_user_files_db_repository(db_session: AsyncSession) -> UserFilesDatabaseRepositoryABC:
    return UserFilesDatabaseRepository(db_session)


def provide_users_retrieve_service(db_repository: UsersDatabaseRepositoryABC) -> UsersRetrieveServiceABC:
    return UsersRetrieveService(db_repository)


def provide_users_create_update_service(
    db_repository: UsersDatabaseRepositoryABC,
    settings: SettingsABC,
) -> UsersCreateUpdateServiceABC:
    return UsersCreateUpdateService(db_repository, settings)


def provide_users_delete_service(db_repository: UsersDatabaseRepositoryABC) -> UsersDeleteServiceABC:
    return UsersDeleteService(db_repository)


def provide_user_files_service(db_repository: UserFilesDatabaseRepositoryABC) -> UserFilesServiceABC:
    return UserFilesService(db_repository)

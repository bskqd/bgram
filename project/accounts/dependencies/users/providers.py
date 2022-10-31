from sqlalchemy.ext.asyncio import AsyncSession

from accounts.database.repository.users import (
    UsersDatabaseRepositoryABC, UserFilesDatabaseRepositoryABC, UsersDatabaseRepository, UserFilesDatabaseRepository,
)
from accounts.services.users import (
    UsersRetrieveService, UsersCreateUpdateService, UserFilesService, UsersRetrieveServiceABC,
    UsersCreateUpdateServiceABC, UserFilesServiceABC,
)
from core.config import SettingsABC


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


def provide_user_files_service(db_repository: UserFilesDatabaseRepositoryABC) -> UserFilesServiceABC:
    return UserFilesService(db_repository)

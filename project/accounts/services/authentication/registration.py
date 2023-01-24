import abc

from accounts.events.authentication import user_registered_event
from accounts.services.authentication.authentication import ConfirmationTokensCreateServiceABC
from accounts.services.exceptions.authentication import ConfirmationTokenCreationException
from accounts.services.users import UsersCreateUpdateServiceABC, UsersDeleteServiceABC


class UsersRegistrationServiceABC(abc.ABC):
    @abc.abstractmethod
    async def registrate_user(self, *args, **kwargs):
        pass


class UsersRegistrationService(UsersRegistrationServiceABC):
    def __init__(
        self,
        user_create_update_service: UsersCreateUpdateServiceABC,
        users_delete_service: UsersDeleteServiceABC,
        create_confirmation_token_service: ConfirmationTokensCreateServiceABC,
    ):
        self._user_create_update_service = user_create_update_service
        self._users_delete_service = users_delete_service
        self._create_confirmation_token_service = create_confirmation_token_service

    async def registrate_user(self, user_nickname: str, user_email: str, user_password: str, **other_user_data):
        other_user_data['is_active'] = False
        user = await self._user_create_update_service.create_user(
            user_nickname,
            user_email,
            user_password,
            **other_user_data,
        )
        try:
            confirmation_token = await self._create_confirmation_token_service.create_confirmation_token(user)
        except ConfirmationTokenCreationException as e:
            await self._users_delete_service.delete_user(user.id)
            raise e
        await user_registered_event(user, confirmation_token)

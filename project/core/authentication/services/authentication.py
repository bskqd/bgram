import abc

from accounts.models import User


class AuthenticationServiceABC(abc.ABC):
    @classmethod
    @abc.abstractmethod
    async def validate_authorization_header(cls, header: str) -> User:
        pass

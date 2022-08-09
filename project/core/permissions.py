import abc
from typing import Optional

from fastapi import HTTPException

from accounts.models import User


class BasePermission(abc.ABC):
    """
    Abstract service class for permissions.
    """

    permission_denied_exception = HTTPException(
        status_code=403,
        detail='You does not have the permission to perform this action',
    )

    @abc.abstractmethod
    async def check_permissions(self):
        """
        Method must be overridden and raise exception in case of not allowed operation.
        """
        pass


class UserIsAuthenticatedPermission(BasePermission):
    def __init__(self, request_user: Optional[User]):
        self.request_user = request_user

    async def check_permissions(self):
        if not self.request_user:
            raise self.permission_denied_exception

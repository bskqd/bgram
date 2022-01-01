from abc import ABC, abstractmethod


class PermissionsServiceABC(ABC):
    """
    Abstract service class for permissions.
    """

    @abstractmethod
    async def check_permissions(self) -> bool:
        """
        Method must return a boolean value indicating whether the action is allowed or not.
        """
        pass

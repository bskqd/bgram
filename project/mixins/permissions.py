class PermissionsRepository:
    """
    Abstract service class for permissions.
    """

    async def check_permissions(self) -> bool:
        """
        Method must return a boolean value indicating whether the action is allowed or not.
        """
        return True

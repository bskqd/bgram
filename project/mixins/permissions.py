from fastapi import HTTPException


class PermissionsRepository:
    """
    Abstract service class for permissions.
    """

    permission_denied_exception = HTTPException(
        status_code=403,
        detail='You does not have the permission to perform this action'
    )

    async def check_permissions(self):
        """
        Method must be overridden and raise exception in case of not allowed operation.
        """
        pass

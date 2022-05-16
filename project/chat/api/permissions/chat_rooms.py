from accounts.models import User
from core.permissions import UserIsAuthenticatedPermission


class ChatRoomPermission:
    def __init__(self, request_user: User):
        self.request_user = request_user

    async def check_permissions(self):
        await UserIsAuthenticatedPermission(self.request_user).check_permissions()

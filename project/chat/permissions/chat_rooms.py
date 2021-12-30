from accounts.models import User


class UserChatRoomMessagingPermissions:
    """
    Permissions class for messaging in chat rooms for user.
    """

    def __init__(self, user: User):
        self.user = user

    def check_permissions(self):
        pass

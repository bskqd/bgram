class UserCreationException(Exception):
    def __init__(self):
        super().__init__('Error during the user creation, probably user with the same nickname or email exists')

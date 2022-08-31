class InvalidConfirmationTokenException(Exception):
    def __init__(self):
        self.message = 'Confirmation token is not valid or expired'

    def __str__(self):
        return repr(self.message)

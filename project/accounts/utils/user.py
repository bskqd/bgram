from core.config import settings


def get_hashed_password(plain_text_password: str) -> bytes:
    # Hashes the password.
    return settings.PWD_CONTEXT.hash(plain_text_password)

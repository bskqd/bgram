from core.config import settings


def hash_password(plain_text_password: str) -> str:
    return settings.PWD_CONTEXT.hash(plain_text_password)

from pydantic import BaseModel


class TokenConfirmationSchema(BaseModel):
    user_id: int
    token: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class LoginSchema(BaseModel):
    email: str
    password: str

from pydantic import BaseModel


class EmailConfirmationSchema(BaseModel):
    token: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class LoginSchema(BaseModel):
    email: str
    password: str

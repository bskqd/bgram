import uuid

from mixins.models import DateTimeABC
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

__all__ = ['EmailConfirmationToken']


def generate_token() -> str:
    return uuid.uuid4().hex


class EmailConfirmationToken(DateTimeABC):
    __tablename__ = 'email_confirmation_tokens'

    token = Column(String, primary_key=True, default=generate_token())
    user_id = Column(Integer, ForeignKey('users.id'), index=True)

    user = relationship('User', back_populates='email_confirmation_tokens', lazy='joined', cascade='all, delete')

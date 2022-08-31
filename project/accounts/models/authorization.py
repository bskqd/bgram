import random

from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from mixins.models import DateTimeABC

__all__ = ['EmailConfirmationToken']


def generate_token() -> str:
    return str(random.randint(1000, 9999))


class EmailConfirmationToken(DateTimeABC):
    __tablename__ = 'email_confirmation_tokens'

    token = Column(String, primary_key=True, default=generate_token())
    user_id = Column(Integer, ForeignKey('users.id'), index=True)

    user = relationship('User', back_populates='email_confirmation_tokens', lazy='joined', cascade='all, delete')

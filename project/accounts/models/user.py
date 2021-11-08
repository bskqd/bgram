from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from core.config import settings
from mixins.models import DateTimeABC, Photo


class User(DateTimeABC):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    nickname = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    description = Column(String, default='')
    is_active = Column(Boolean, default=True)

    email_confirmation_tokens = relationship('EmailConfirmationToken', back_populates='user')
    photos = relationship('UserPhoto', back_populates='user', lazy='joined')

    def check_password(self, plain_text_password: str) -> bool:
        # Checks if plain texted password is the same as the user password.
        return settings.PWD_CONTEXT.verify(plain_text_password, self.password)


class UserPhoto(Photo):
    __tablename__ = 'users_photos'

    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='photos', lazy='joined', cascade='all, delete')

    @property
    def folder_to_save(self) -> str:
        """
        Returns path to directory where to save a file.
        """
        return f'users/{self.user_id}/'

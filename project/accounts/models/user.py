from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from chat.models import chatroom_members_association_table
from core.config import settings
from mixins.models import DateTimeABC, PhotoABC, DescriptionABC, IsActiveABC

__all__ = ['User', 'UserPhoto']


class User(DateTimeABC, DescriptionABC, IsActiveABC):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    nickname = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)

    email_confirmation_tokens = relationship('EmailConfirmationToken', back_populates='user')
    photos = relationship('UserPhoto', back_populates='user')
    chat_rooms = relationship(
        'ChatRoom', secondary=chatroom_members_association_table, back_populates='members'
    )

    def check_password(self, plain_text_password: str) -> bool:
        # Checks if plain texted password is the same as the user password.
        return settings.PWD_CONTEXT.verify(plain_text_password, self.password)


class UserPhoto(PhotoABC):
    __tablename__ = 'users_photos'

    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='photos', cascade='all, delete')

    @property
    def folder_to_save(self) -> str:
        """
        Returns path to directory where to save a file.
        """
        return f'users/{self.user_id}/'

from chat.models import chatroom_members_association_table
from core.dependencies.providers import provide_settings
from mixins.models import DateTimeABC, DescriptionABC, FileABC, IsActiveABC
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

__all__ = ['User', 'UserFile']


class User(DateTimeABC, DescriptionABC, IsActiveABC):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    nickname = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)

    email_confirmation_tokens = relationship('EmailConfirmationToken', back_populates='user')
    photos = relationship('UserFile', back_populates='user')
    messages = relationship('Message', back_populates='author')
    chat_rooms = relationship(
        'ChatRoom',
        secondary=chatroom_members_association_table,
        back_populates='members',
    )

    def check_password(self, plain_text_password: str) -> bool:
        return provide_settings().PWD_CONTEXT.verify(plain_text_password, self.password)


class UserFile(FileABC):
    __tablename__ = 'users_photos'

    user_id = Column(Integer, ForeignKey('users.id'), index=True)

    user = relationship('User', back_populates='photos', cascade='all, delete')

    @property
    def folder_to_save(self) -> str:
        return f'users/{super().folder_to_save}'

from sqlalchemy import Column, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from mixins.models import DateTimeABC, PhotoABC

__all__ = ['Message', 'MessagePhoto']


class Message(DateTimeABC):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    is_edited = Column(Boolean, default=False)
    text = Column(Text, default='')
    author_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    chat_room_id = Column(Integer, ForeignKey('chat_rooms.id'), index=True)
    replayed_message_id = Column(Integer, ForeignKey('messages.id', ondelete='SET NULL'), index=True)

    author = relationship('User', back_populates='messages')
    chat_room = relationship('ChatRoom', back_populates='messages', cascade='all, delete')
    replayed_message = relationship('Message', remote_side=id, backref='replies')
    photos = relationship('MessagePhoto', back_populates='message')


class MessagePhoto(PhotoABC):
    __tablename__ = 'message_photos'

    message_id = Column(Integer, ForeignKey('messages.id'), index=True)

    message = relationship('Message', back_populates='photos', cascade='all, delete')

    @property
    def folder_to_save(self) -> str:
        """
        Returns path to directory where to save a file.
        """
        return f'message/{self.message_id}/'

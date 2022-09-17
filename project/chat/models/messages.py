from sqlalchemy import Column, Integer, ForeignKey, Boolean, Text, DateTime, String
from sqlalchemy.orm import relationship

from chat.constants.messages import MessagesTypeEnum
from mixins.models import DateTimeABC, FileABC

__all__ = ['Message', 'MessageFile']


class Message(DateTimeABC):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    is_edited = Column(Boolean, default=False)
    text = Column(Text, default='')
    author_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    chat_room_id = Column(Integer, ForeignKey('chat_rooms.id'), index=True)
    replayed_message_id = Column(Integer, ForeignKey('messages.id', ondelete='SET NULL'), index=True)
    message_type = Column(String, nullable=False, default=MessagesTypeEnum.PRIMARY)

    scheduled_at = Column(DateTime)
    scheduler_task_id = Column(
        String,
        index=True,
        doc=(
            'If the message is scheduled, then id of the scheduled task in the scheduler '
            'must be saved here for the future use'
        ),
    )

    author = relationship('User', back_populates='messages')
    chat_room = relationship('ChatRoom', back_populates='messages', cascade='all, delete')
    replayed_message = relationship('Message', remote_side=id, backref='replies')
    photos = relationship('MessageFile', back_populates='message')


class MessageFile(FileABC):
    __tablename__ = 'message_photos'

    message_id = Column(Integer, ForeignKey('messages.id', ondelete='CASCADE'), index=True)

    message = relationship('Message', back_populates='photos', cascade='all, delete')

    @property
    def folder_to_save(self) -> str:
        return f'messages/{super().folder_to_save}'

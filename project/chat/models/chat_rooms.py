from sqlalchemy import Column, Integer, String, Table, ForeignKey, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import func

from chat.constants import chat_rooms as chat_rooms_constants
from database import Base
from mixins.models import DateTimeABC, DescriptionABC, IsActiveABC, PhotoABC

__all__ = ['chatroom_members_association_table', 'ChatRoom', 'ChatRoomPhoto']


chatroom_members_association_table = Table(
    'chatroom_members_association',
    Base.metadata,
    Column('room_id', Integer, ForeignKey('chat_rooms.id', ondelete='CASCADE'), index=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True),
    Column('member_type', String, nullable=False, default=chat_rooms_constants.ChatRoomMemberTypeEnum.MEMBER.value)
)


class ChatRoom(DateTimeABC, DescriptionABC, IsActiveABC):
    __tablename__ = 'chat_rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    photos = relationship('ChatRoomPhoto', back_populates='chat_room')
    members = relationship(
        'User', secondary=chatroom_members_association_table, back_populates='chat_rooms'
    )
    messages = relationship('Message', back_populates='chat_room')

    @hybrid_property
    def members_count(self):
        return len(self.members)

    @members_count.expression
    def members_count(self):
        return select(
            func.count(chatroom_members_association_table.c.room_id)
        ).join(
            ChatRoom, chatroom_members_association_table.c.room_id == ChatRoom.id
        ).where(
            chatroom_members_association_table.c.room_id == self.id
        ).group_by(
            chatroom_members_association_table.c.room_id
        ).subquery()


class ChatRoomPhoto(PhotoABC):
    __tablename__ = 'chat_rooms_photos'

    chat_room_id = Column(Integer, ForeignKey('chat_rooms.id'))

    chat_room = relationship('ChatRoom', back_populates='photos', cascade='all, delete')

    @property
    def folder_to_save(self) -> str:
        """
        Returns path to directory where to save a file.
        """
        return f'chat_room/{self.chat_room_id}/'

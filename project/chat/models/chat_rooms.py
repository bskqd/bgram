from chat.constants import chat_rooms as chat_rooms_constants
from core.database.base import Base
from mixins.models import DateTimeABC, DescriptionABC, FileABC, IsActiveABC
from sqlalchemy import Column, ForeignKey, Integer, String, Table, event, func, select
from sqlalchemy.orm import aliased, column_property, mapper, relationship

__all__ = ['chatroom_members_association_table', 'ChatRoom', 'ChatRoomFile']


chatroom_members_association_table = Table(
    'chatroom_members_association',
    Base.metadata,
    Column('room_id', Integer, ForeignKey('chat_rooms.id', ondelete='CASCADE'), index=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True),
    Column('member_type', String, nullable=False, default=chat_rooms_constants.ChatRoomMemberTypeEnum.MEMBER.value),
)


class ChatRoom(DateTimeABC, DescriptionABC, IsActiveABC):
    __tablename__ = 'chat_rooms'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    photos = relationship('ChatRoomFile', back_populates='chat_room')
    members = relationship(
        'User',
        secondary=chatroom_members_association_table,
        back_populates='chat_rooms',
    )
    messages = relationship('Message', back_populates='chat_room')


@event.listens_for(mapper, 'mapper_configured')
def set_thread_count(mapper, cls) -> None:
    if not issubclass(cls, ChatRoom):
        return

    nested_chat_room = aliased(ChatRoom)
    members_count_subquery = (
        select(
            func.count(chatroom_members_association_table.c.member_type).label('members_count'),
        )
        .select_from(
            chatroom_members_association_table,
        )
        .join(
            nested_chat_room,
        )
        .group_by(
            nested_chat_room.id,
        )
        .where(nested_chat_room.id == ChatRoom.id)
        .scalar_subquery()
    )
    cls.members_count = column_property(members_count_subquery)


class ChatRoomFile(FileABC):
    __tablename__ = 'chat_rooms_photos'

    chat_room_id = Column(Integer, ForeignKey('chat_rooms.id'), index=True)

    chat_room = relationship('ChatRoom', back_populates='photos', cascade='all, delete')

    @property
    def folder_to_save(self) -> str:
        return f'chat_room/{super().folder_to_save}'

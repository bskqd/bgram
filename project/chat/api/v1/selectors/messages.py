from sqlalchemy import select
from sqlalchemy.orm import contains_eager, joinedload
from sqlalchemy.sql import Select
from fastapi import Request

from chat.models import Message


def get_messages_db_query(request: Request, chat_room_id: int, *args) -> Select:
    db_query = select(
        Message
    ).join(
        Message.author
    ).where(
        Message.chat_room_id == chat_room_id, *args
    ).order_by(-Message.id)
    if request.method == 'GET':
        return db_query.options(joinedload(Message.photos), contains_eager(Message.author))
    return db_query.options(joinedload(Message.photos), joinedload(Message.author))

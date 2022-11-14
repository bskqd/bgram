import functools

from chat.models import Message, MessageFile
from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import contains_eager, joinedload
from sqlalchemy.sql import Select


def get_messages_db_query_by_chat_room_id(
    request: Request, chat_room_id: int, *args, load_relationships: bool = True
) -> Select:
    db_query = (
        select(
            Message,
        )
        .join(
            Message.author,
        )
        .where(
            *args,
            Message.chat_room_id == chat_room_id,
        )
        .order_by(-Message.id)
    )
    if not load_relationships:
        return db_query
    if request.method == 'GET':
        return db_query.options(joinedload(Message.photos), contains_eager(Message.author))
    return db_query.options(joinedload(Message.photos), joinedload(Message.author))


def get_message_db_query(*args, load_relationships: bool = True) -> Select:
    db_query = select(Message).where(*args).order_by(-Message.id)
    if not load_relationships:
        return db_query
    return db_query.options(joinedload(Message.photos), joinedload(Message.author))


def get_message_file_db_query(*args, load_relationships: bool = True) -> Select:
    db_query = select(MessageFile).where(*args)
    if not load_relationships:
        return db_query
    return db_query.options(joinedload(MessageFile.message).load_only(Message.id, Message.message_type))


@functools.lru_cache(maxsize=1)
def get_message_creation_relations_to_load() -> tuple:
    return (
        joinedload(Message.author),
        joinedload(Message.photos),
    )

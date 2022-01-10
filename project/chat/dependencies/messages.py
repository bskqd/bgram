from fastapi import Request
from sqlalchemy import select
from sqlalchemy.sql import Select

from chat.models import Message


async def get_messages_queryset(request: Request) -> Select:
    return select(Message)

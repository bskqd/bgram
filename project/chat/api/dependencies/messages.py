from fastapi import Request

from chat.api.v1.filters.messages import MessagesFilterSet
from core.filters import FilterSet


async def get_messages_filterset(request: Request) -> FilterSet:
    return MessagesFilterSet(request=request)
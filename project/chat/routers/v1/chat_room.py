from typing import Optional

from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.orm import Session

from chat.dependencies import chat_room as chat_room_dependencies
from mixins import views as mixins_views, dependencies as mixins_dependencies

router = APIRouter()


@cbv(router)
class ChatRoomView(mixins_views.AbstractView):
    available_db_data: ChunkedIteratorResult = Depends(chat_room_dependencies.available_db_data)
    db_session: Optional[Session] = Depends(mixins_dependencies.db_session)

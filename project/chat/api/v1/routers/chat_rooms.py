from accounts.models import User
from chat.api.pagination.chat_rooms import ChatRoomsPaginatorABC
from chat.api.permissions.chat_rooms import ChatRoomPermission
from chat.api.v1.schemas.chat_rooms import (
    ChatRoomCreateSchema,
    ChatRoomDetailSchema,
    ChatRoomUpdateSchema,
    PaginatedChatRoomsListSchema,
)
from chat.database.selectors.chat_rooms import get_chat_room_creation_relations_to_load, get_chat_rooms_db_query
from chat.models import ChatRoom
from chat.services.chat_rooms import ChatRoomsCreateUpdateServiceABC, ChatRoomsRetrieveServiceABC
from fastapi import APIRouter, Depends

router = APIRouter()


# TODO: perform members count in db
@router.get('/chat_rooms', response_model=PaginatedChatRoomsListSchema)
async def list_chat_rooms_view(request_user: User = Depends(), paginator: ChatRoomsPaginatorABC = Depends()):
    await ChatRoomPermission(request_user).check_permissions()
    return await paginator.paginate(get_chat_rooms_db_query(request_user))


@router.get('/chat_rooms/{chat_room_id}', response_model=ChatRoomDetailSchema)
async def retrieve_chat_room_view(
    chat_room_id: int,
    request_user: User = Depends(),
    chat_rooms_retrieve_service: ChatRoomsRetrieveServiceABC = Depends(),
):
    await ChatRoomPermission(request_user).check_permissions()
    return await chat_rooms_retrieve_service.get_one_chat_room(
        ChatRoom.id == chat_room_id,
        db_query=get_chat_rooms_db_query(request_user),
    )


@router.post('/chat_rooms', response_model=ChatRoomDetailSchema)
async def create_chat_room_view(
    chat_room_data: ChatRoomCreateSchema,
    request_user: User = Depends(),
    chat_rooms_create_service: ChatRoomsCreateUpdateServiceABC = Depends(),
):
    await ChatRoomPermission(request_user).check_permissions()
    chat_room_data = chat_room_data.dict()
    name = chat_room_data.pop('name')
    members = chat_room_data.pop('members', [])
    return await chat_rooms_create_service.create_chat_room(
        name,
        members,
        relations_to_load_after_creation=get_chat_room_creation_relations_to_load(),
        **chat_room_data,
    )


@router.patch('/chat_rooms/{chat_room_id}', response_model=ChatRoomDetailSchema)
async def update_chat_room_view(
    chat_room_id: int,
    chat_room_data: ChatRoomUpdateSchema,
    request_user: User = Depends(),
    chat_rooms_update_service: ChatRoomsCreateUpdateServiceABC = Depends(),
    chat_rooms_retrieve_service: ChatRoomsRetrieveServiceABC = Depends(),
):
    await ChatRoomPermission(request_user).check_permissions()
    chat_room = await chat_rooms_retrieve_service.get_one_chat_room(
        ChatRoom.id == chat_room_id,
        db_query=get_chat_rooms_db_query(request_user),
    )
    chat_room_data: dict = chat_room_data.dict(exclude_unset=True)
    members_ids = chat_room_data.pop('members', None)
    return await chat_rooms_update_service.update_chat_room(chat_room, members_ids=members_ids, **chat_room_data)

from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from chat.events.messages import message_created_event, message_updated_event, message_deleted_event
from chat.models import Message, MessagePhoto
from database.repository import BaseCRUDRepository
from mixins.services.files import FilesService


class MessagesService:
    def __init__(
            self,
            db_repository: BaseCRUDRepository,
            chat_room_id: Optional[int] = None
    ):
        self.db_repository = db_repository
        self.chat_room_id = chat_room_id

    async def create_message(
            self,
            text: str,
            files: Optional[List[UploadFile]] = None,
            author_id: Optional[int] = None,
            **kwargs
    ) -> Message:
        message = Message(chat_room_id=self.chat_room_id, text=text, author_id=author_id, **kwargs)
        created_message = await self.db_repository.create(message)
        await self.db_repository.commit()
        await self.db_repository.refresh(created_message)
        message_id = created_message.id
        files_service = FilesService(self.db_repository, MessagePhoto)
        for file in files:
            await files_service.create_object_file(file, message_id=message_id)
        self.db_repository.db_query = select(Message).options(joinedload(Message.photos))
        created_message = await self.db_repository.get_one(Message.id == message_id)
        await message_created_event(created_message)
        return created_message

    async def update_message(self, message: Message, **kwargs) -> Message:
        if not message.is_edited:
            kwargs['is_edited'] = True
        updated_message = await self.db_repository.update_object(message, **kwargs)
        await self.db_repository.commit()
        await self.db_repository.refresh(updated_message)
        await message_updated_event(updated_message)
        return updated_message

    async def delete_message(self, message_id: int) -> int:
        await self.db_repository.delete(Message.id == message_id)
        await message_deleted_event(self.chat_room_id, message_id)
        return message_id


# class MessagesFilesServices:
#     def __init__(
#             self,
#             message: Message,
#             db_repository: BaseCRUDRepository,
#             broadcast_message_to_chat_room: bool = True
#     ):
#         self.message = message
#         self.db_repository = db_repository
#         self.broadcast_message_to_chat_room = broadcast_message_to_chat_room
#
#     async def delete_message_file(self, file_id: int):
#         await self.db_repository.delete(MessagePhoto.id == file_id)
#         if self.broadcast_message_to_chat_room:
#             await message_updated_event(updated_message)
#
#     async def create_message_

from typing import Optional, Tuple

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from chat.events.messages import message_created_event, message_updated_event, messages_deleted_event
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
            files: Optional[Tuple[UploadFile]] = None,
            author_id: Optional[int] = None,
            **kwargs
    ) -> Message:
        message = Message(chat_room_id=self.chat_room_id, text=text, author_id=author_id, **kwargs)
        created_message = await self.db_repository.create(message)
        await self.db_repository.commit()
        await self.db_repository.refresh(created_message)
        message_id = created_message.id
        files_service = FilesService(self.db_repository, MessagePhoto)
        if files:
            for file in files:
                await files_service.create_object_file(file, message_id=message_id)
        self.db_repository.db_query = select(Message).options(joinedload(Message.author), joinedload(Message.photos))
        created_message = await self.db_repository.get_one(Message.id == message_id)
        await message_created_event(created_message, self.db_repository)
        return created_message

    async def update_message(self, message: Message, **kwargs) -> Message:
        if not message.is_edited:
            kwargs['is_edited'] = True
        updated_message = await self.db_repository.update_object(message, **kwargs)
        await self.db_repository.commit()
        await self.db_repository.refresh(updated_message)
        await message_updated_event(updated_message, self.db_repository)
        return updated_message

    async def delete_messages(self, message_ids: list[int]) -> list[int]:
        await self.db_repository.delete(Message.id.in_(message_ids))
        await self.db_repository.commit()
        await messages_deleted_event(self.chat_room_id, message_ids)
        return message_ids


class MessagesFilesServices:
    def __init__(self, message_id: int, message_file_id: int, db_repository: BaseCRUDRepository):
        self.message_id = message_id
        self.message_file_id = message_file_id
        self.db_repository = db_repository

    async def change_message_file(self, replacement_file: UploadFile) -> MessagePhoto:
        new_message_file: MessagePhoto = await FilesService(
            self.db_repository,
            MessagePhoto
        ).change_file(self.message_file_id, replacement_file)
        await message_updated_event(self.message_id, self.db_repository)
        return new_message_file

    async def delete_message_file(self):
        await FilesService(self.db_repository, MessagePhoto).delete_file_object(self.message_file_id)
        await message_updated_event(self.message_id, self.db_repository)

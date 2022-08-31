import abc
from typing import Optional, Tuple

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from chat.events.messages import message_created_event, message_updated_event, messages_deleted_event
from chat.models import Message, MessagePhoto
from core.database.repository import BaseDatabaseRepository
from core.dependencies import EventPublisher
from core.services.files import FilesService
from mixins.models import PhotoABC


class MessagesRetrieveServiceABC(abc.ABC):
    @abc.abstractmethod
    async def get_one_message(self, *args, db_query: Optional[Select] = None) -> Message:
        pass

    @abc.abstractmethod
    async def get_many_messages(self, *args, db_query: Optional[Select] = None) -> list[Message]:
        pass

    @abc.abstractmethod
    async def count_messages(self, *args, db_query: Optional[Select] = None) -> int:
        pass


class MessagesRetrieveService(MessagesRetrieveServiceABC):
    def __init__(self, db_repository: BaseDatabaseRepository):
        self.db_repository = db_repository

    async def get_one_message(self, *args, db_query: Optional[Select] = None) -> Message:
        return await self.db_repository.get_one(*args, db_query=db_query)

    async def get_many_messages(self, *args, db_query: Optional[Select] = None) -> list[Message]:
        return await self.db_repository.get_many(*args, db_query=db_query)

    async def count_messages(self, *args, db_query: Optional[Select] = None) -> int:
        return await self.db_repository.count(*args, db_query=db_query)


class MessagesCreateUpdateDeleteServiceABC(abc.ABC):
    @abc.abstractmethod
    async def create_message(self, *args, **kwargs) -> Message:
        pass

    @abc.abstractmethod
    async def update_message(self, *args, **kwargs) -> Message:
        pass

    @abc.abstractmethod
    async def delete_messages(self, *args) -> tuple[int]:
        pass


class MessagesCreateUpdateDeleteService(MessagesCreateUpdateDeleteServiceABC):
    def __init__(
            self,
            db_repository: BaseDatabaseRepository,
            chat_room_id: Optional[int] = None,
            event_publisher: Optional[EventPublisher] = None,
            message_files_service: Optional['MessageFilesServiceABC'] = None,
    ):
        self.db_repository = db_repository
        self.chat_room_id = chat_room_id
        self.event_publisher = event_publisher
        self.message_files_service = message_files_service

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
        if files:
            for file in files:
                await self.message_files_service.create_object_file(file, message_id=message_id)
        created_message = await self.db_repository.get_one(
            db_query=select(Message).options(
                joinedload(Message.author), joinedload(Message.photos)
            ).where(Message.id == message_id)
        )
        await message_created_event(self.event_publisher, created_message)
        return created_message

    async def update_message(self, message: Message, **kwargs) -> Message:
        if not message.is_edited:
            kwargs['is_edited'] = True
        updated_message = await self.db_repository.update_object(message, **kwargs)
        await self.db_repository.commit()
        await self.db_repository.refresh(updated_message)
        await message_updated_event(self.event_publisher, updated_message)
        return updated_message

    async def delete_messages(self, message_ids: tuple[int]) -> tuple[int]:
        await self.db_repository.delete(Message.id.in_(message_ids))
        await self.db_repository.commit()
        await messages_deleted_event(self.event_publisher, self.chat_room_id, message_ids)
        return message_ids


class MessageFilesRetrieveServiceABC(abc.ABC):
    @abc.abstractmethod
    async def get_one_message_file(self, *args, db_query: Optional[Select] = None) -> Message:
        pass


class MessageFilesRetrieveService(MessageFilesRetrieveServiceABC):
    def __init__(self, db_repository: BaseDatabaseRepository):
        self.db_repository = db_repository

    async def get_one_message_file(self, *args, db_query: Optional[Select] = None) -> Message:
        return await self.db_repository.get_one(*args, db_query=db_query)


class MessageFilesServiceABC(abc.ABC):
    @abc.abstractmethod
    async def create_object_file(self, file: UploadFile, **kwargs) -> PhotoABC:
        pass

    @abc.abstractmethod
    async def change_message_file(self, replacement_file: UploadFile) -> PhotoABC:
        pass

    @abc.abstractmethod
    async def delete_message_file(self):
        pass


class MessageFilesService(MessageFilesServiceABC, FilesService):
    file_model = MessagePhoto

    def __init__(
            self,
            db_repository: BaseDatabaseRepository,
            message_file: MessagePhoto,
            event_publisher: EventPublisher,
    ):
        super().__init__(db_repository)
        self.message_file = message_file
        self.message = message_file.message
        self.event_publisher = event_publisher

    async def change_message_file(self, replacement_file: UploadFile) -> MessagePhoto:
        new_message_file: MessagePhoto = await super().change_file(self.message_file.id, replacement_file)
        await message_updated_event(self.event_publisher, self.message)
        return new_message_file

    async def delete_message_file(self):
        await super().delete_file_object(self.message_file.id)
        await message_updated_event(self.event_publisher, self.message)

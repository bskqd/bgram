import abc
from typing import Optional

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select

from chat.constants.messages import MessagesTypeEnum
from chat.events.messages import message_created_event, message_updated_event, messages_deleted_event
from chat.models import Message, MessageFile
from core.database.repository import BaseDatabaseRepository
from core.dependencies import EventPublisher
from core.services.files import FilesService
from core.tasks_scheduling.dependencies import TasksScheduler
from mixins.models import FileABC


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
    async def create_scheduled_message(self, *args, **kwargs) -> Message:
        pass

    @abc.abstractmethod
    async def update_message(self, *args, **kwargs) -> Message:
        pass

    @abc.abstractmethod
    async def update_scheduled_message(self, *args, **kwargs) -> Message:
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
            tasks_scheduler: Optional[TasksScheduler] = None,
    ):
        self._db_repository = db_repository
        self._chat_room_id = chat_room_id
        self._event_publisher = event_publisher
        self._message_files_service = message_files_service
        self._tasks_scheduler = tasks_scheduler

    async def create_message(
            self,
            text: str,
            files: Optional[tuple[UploadFile]] = None,
            author_id: Optional[int] = None,
            load_relations_after_creation: bool = True,
            **kwargs
    ) -> Message:
        created_message = await self._create_message(
            text, files, author_id, message_type=MessagesTypeEnum.PRIMARY.value, **kwargs
        )
        await message_created_event(self._event_publisher, created_message)
        return created_message

    async def create_scheduled_message(
            self,
            text: str,
            files: Optional[tuple[UploadFile]] = None,
            author_id: Optional[int] = None,
            load_relations_after_creation: bool = True,
            **kwargs
    ) -> Message:
        created_message = await self._create_message(
            text, files, author_id, message_type=MessagesTypeEnum.SCHEDULED.value,
            load_relations_after_creation=False, **kwargs,
        )
        await self._db_repository.refresh(created_message)
        task_result = await self._tasks_scheduler.enqueue_job(
            'execute_task_in_background',
            'chat.tasks.messages.send_scheduled_message', task_kwargs={'scheduled_message_id': created_message.id},
            _queue_name='arq:tasks_scheduling_queue', _defer_until=created_message.scheduled_at,
        )
        await self.update_scheduled_message(created_message, scheduler_task_id=task_result.job_id)
        if load_relations_after_creation:
            created_message = await self._load_message_relations(created_message.id)
        return created_message

    async def _create_message(
            self,
            text: str,
            files: Optional[tuple[UploadFile]] = None,
            author_id: Optional[int] = None,
            load_relations_after_creation: bool = True,
            **kwargs
    ) -> Message:
        message = Message(chat_room_id=self._chat_room_id, text=text, author_id=author_id, **kwargs)
        created_message = await self._db_repository.create(message)
        await self._db_repository.commit()
        await self._db_repository.refresh(created_message)
        message_id = created_message.id
        if files:
            for file in files:
                await self._message_files_service.create_object_file(file, message_id=message_id)
        if load_relations_after_creation:
            return await self._load_message_relations(message_id)
        return created_message

    async def _load_message_relations(self, message_id: int) -> Message:
        return await self._db_repository.get_one(
            db_query=select(Message).options(
                joinedload(Message.author), joinedload(Message.photos),
            ).where(Message.id == message_id),
        )

    async def update_message(self, message: Message, **kwargs) -> Message:
        if not message.is_edited:
            kwargs['is_edited'] = True
        updated_message = await self._db_repository.update_object(message, **kwargs)
        await self._db_repository.commit()
        await self._db_repository.refresh(updated_message)
        await message_updated_event(self._event_publisher, updated_message)
        return updated_message

    async def update_scheduled_message(self, message: Message, **kwargs):
        # TODO: implement task rescheduling
        updated_message = await self._db_repository.update_object(message, **kwargs)
        await self._db_repository.commit()
        await self._db_repository.refresh(updated_message)
        return updated_message

    async def delete_messages(self, message_ids: tuple[int]) -> tuple[int]:
        await self._db_repository.delete(Message.id.in_(message_ids))
        await self._db_repository.commit()
        await messages_deleted_event(self._event_publisher, self._chat_room_id, message_ids)
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
    async def create_object_file(self, file: UploadFile, **kwargs) -> FileABC:
        pass

    @abc.abstractmethod
    async def change_message_file(self, replacement_file: UploadFile) -> FileABC:
        pass

    @abc.abstractmethod
    async def delete_message_file(self):
        pass


class MessageFilesService(FilesService, MessageFilesServiceABC):
    file_model = MessageFile

    def __init__(
            self,
            db_repository: BaseDatabaseRepository,
            message_file: Optional[MessageFile],
            event_publisher: EventPublisher,
    ):
        super().__init__(db_repository)
        self.message_file = message_file
        self.message = message_file.message if self.message_file else None
        self.event_publisher = event_publisher

    async def change_message_file(self, replacement_file: UploadFile) -> MessageFile:
        new_message_file: MessageFile = await super().change_file(self.message_file.id, replacement_file)
        await message_updated_event(self.event_publisher, self.message)
        return new_message_file

    async def delete_message_file(self):
        await super().delete_file_object(self.message_file.id)
        await message_updated_event(self.event_publisher, self.message)

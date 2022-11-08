import abc
import asyncio.exceptions
from typing import Optional, Union

from chat.constants.messages import MessagesTypeEnum
from chat.events.messages import message_created_event, message_updated_event, messages_deleted_event
from chat.models import Message, MessageFile
from chat.services.exceptions.messages import MissingTasksSchedulerException
from core.database.repository import BaseDatabaseRepository
from core.dependencies.providers import EventPublisher
from core.services.files import FilesService, FilesServiceABC
from core.tasks_scheduling.dependencies import JobResult, TasksSchedulerABC
from fastapi import UploadFile
from mixins.models import FileABC
from sqlalchemy import select
from sqlalchemy.sql import Select


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

    @abc.abstractmethod
    async def delete_scheduled_messages(self, *args) -> tuple[int]:
        pass


class MessagesCreateUpdateDeleteService(MessagesCreateUpdateDeleteServiceABC):
    def __init__(
        self,
        db_repository: BaseDatabaseRepository,
        chat_room_id: Optional[int],
        event_publisher: EventPublisher,
        message_files_service: 'MessageFilesServiceABC',
        tasks_scheduler: Optional[TasksSchedulerABC] = None,
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
        relations_to_load_after_creation: Optional[tuple] = None,
        **kwargs,
    ) -> Message:
        created_message = await self._create_message(
            text,
            files,
            author_id,
            message_type=MessagesTypeEnum.PRIMARY.value,
            relations_to_load_after_creation=relations_to_load_after_creation,
            **kwargs,
        )
        await message_created_event(self._event_publisher, created_message)
        return created_message

    async def create_scheduled_message(
        self,
        text: str,
        files: Optional[tuple[UploadFile]] = None,
        author_id: Optional[int] = None,
        relations_to_load_after_creation: Optional[tuple] = None,
        **kwargs,
    ) -> Message:
        self._check_tasks_scheduler()
        created_message = await self._create_message(
            text,
            files,
            author_id,
            message_type=MessagesTypeEnum.SCHEDULED.value,
            **kwargs,
        )
        task_result = await self._schedule_message(created_message)
        await self.update_scheduled_message(created_message, scheduler_task_id=task_result.job_id)
        if relations_to_load_after_creation:
            created_message = await self._load_message_relations(
                created_message.id,
                relations_to_load=relations_to_load_after_creation,
            )
        return created_message

    async def _create_message(
        self,
        text: str,
        files: Optional[tuple[UploadFile]] = None,
        author_id: Optional[int] = None,
        relations_to_load_after_creation: Optional[tuple] = None,
        **kwargs,
    ) -> Message:
        message = Message(chat_room_id=self._chat_room_id, text=text, author_id=author_id, **kwargs)
        created_message = await self._db_repository.create_from_object(message)
        await self._db_repository.commit()
        if files:
            for file in files:
                await self._message_files_service.create_object_file(file, message_id=created_message.id)
        if relations_to_load_after_creation:
            return await self._load_message_relations(created_message.id, relations_to_load_after_creation)
        return created_message

    async def _load_message_relations(self, message_id: int, relations_to_load: Optional[tuple] = None) -> Message:
        return await self._db_repository.get_one(
            db_query=select(Message).options(*relations_to_load).where(Message.id == message_id),
        )

    async def update_message(
        self,
        message: Union[Message, int],
        mark_as_edited: bool = True,
        _returning_options: Optional[tuple] = None,
        **kwargs,
    ) -> Message:
        if mark_as_edited and not message.is_edited:
            kwargs['is_edited'] = True
        updated_message = await self._update_message(message, _returning_options, **kwargs)
        await message_updated_event(self._event_publisher, updated_message)
        return updated_message

    async def update_scheduled_message(
        self,
        message: Union[Message, int],
        _returning_options: Optional[tuple] = None,
        **kwargs,
    ) -> Message:
        self._check_tasks_scheduler()
        updated_message = await self._update_message(message, _returning_options, **kwargs)
        await self._schedule_message(updated_message)
        return updated_message

    async def _update_message(
        self,
        message: Union[Message, int],
        _returning_options: Optional[tuple] = None,
        **kwargs,
    ) -> Message:
        if isinstance(message, int):
            updated_message = await self._db_repository.update(
                Message.id == message,
                _returning_options=_returning_options,
                **kwargs,
            )
        else:
            updated_message = await self._db_repository.update_object(message, **kwargs)
        await self._db_repository.commit()
        await self._db_repository.refresh(updated_message)
        return updated_message

    def _check_tasks_scheduler(self):
        if not self._tasks_scheduler:
            raise MissingTasksSchedulerException

    async def _schedule_message(self, message: Message) -> JobResult:
        return await self._tasks_scheduler.enqueue_job(
            'send_scheduled_message',
            message.id,
            _queue_name='arq:tasks_scheduling_queue',
            _defer_until=message.scheduled_at,
            _job_id=message.scheduler_task_id,
        )

    async def delete_messages(self, message_ids: tuple[int]) -> tuple[int]:
        await self._delete_messages(message_ids, Message.message_type == MessagesTypeEnum.PRIMARY.value)
        await messages_deleted_event(self._event_publisher, self._chat_room_id, message_ids)
        return message_ids

    async def delete_scheduled_messages(self, message_ids: tuple[int]) -> tuple[int]:
        self._check_tasks_scheduler()
        task_ids = await self._db_repository.get_many(
            db_query=select(Message.scheduler_task_id).where(
                Message.id.in_(message_ids),
                Message.message_type == MessagesTypeEnum.SCHEDULED.value,
                Message.scheduler_task_id.is_not(None),
            ),
        )
        await self._delete_messages(message_ids, Message.message_type == MessagesTypeEnum.SCHEDULED.value)
        for task_id in task_ids:
            try:
                await self._tasks_scheduler.cancel_job(task_id)
            except asyncio.exceptions.TimeoutError:
                pass
        return message_ids

    async def _delete_messages(
        self,
        message_ids: tuple[int],
        *filtering_args,
        returning_fields: Optional[tuple] = None,
    ) -> list:
        returning = await self._db_repository.delete(
            Message.id.in_(message_ids),
            *filtering_args,
            _returning_fields=returning_fields,
        )
        await self._db_repository.commit()
        await self._message_files_service.delete_message_files_from_filesystem(Message.id.in_(message_ids))
        return returning


class MessageFilesRetrieveServiceABC(abc.ABC):
    @abc.abstractmethod
    async def get_one_message_file(self, *args, db_query: Optional[Select] = None) -> Message:
        pass


class MessageFilesRetrieveService(MessageFilesRetrieveServiceABC):
    def __init__(self, db_repository: BaseDatabaseRepository):
        self.db_repository = db_repository

    async def get_one_message_file(self, *args, db_query: Optional[Select] = None) -> Message:
        return await self.db_repository.get_one(*args, db_query=db_query)


class MessageFilesFilesystemServiceABC(FilesServiceABC, abc.ABC):
    pass


class MessageFilesFilesystemService(FilesService, MessageFilesFilesystemServiceABC):
    file_model = MessageFile


class MessageFilesServiceABC(abc.ABC):
    @abc.abstractmethod
    async def create_object_file(self, file: UploadFile, **kwargs) -> FileABC:
        pass

    @abc.abstractmethod
    async def change_message_file(self, replacement_file: UploadFile, message_file: Union[MessageFile, int]) -> FileABC:
        pass

    @abc.abstractmethod
    async def delete_message_file(self, message_file: Union[MessageFile, int]):
        pass

    @abc.abstractmethod
    async def change_scheduled_message_file(
        self,
        replacement_file: UploadFile,
        message_file: Union[MessageFile, int],
    ) -> FileABC:
        pass

    @abc.abstractmethod
    async def delete_scheduled_message_file(self, message_file: Union[MessageFile, int]):
        pass

    @abc.abstractmethod
    async def delete_message_files_from_filesystem(self, *args):
        pass

    @abc.abstractmethod
    async def get_one_message_file(self, *args, db_query: Optional[Select] = None) -> MessageFile:
        pass

    @abc.abstractmethod
    async def get_many_message_files(self, *args, db_query: Optional[Select] = None) -> list[MessageFile]:
        pass


class MessageFilesService(MessageFilesServiceABC):
    def __init__(
        self,
        files_service: MessageFilesFilesystemServiceABC,
        db_repository: BaseDatabaseRepository,
        event_publisher: Optional[EventPublisher] = None,
    ):
        self.files_service = files_service
        self.db_repository = db_repository
        self.event_publisher = event_publisher

    async def get_one_message_file(self, *args, db_query: Optional[Select] = None) -> MessageFile:
        return await self.db_repository.get_one(*args, db_query=db_query)

    async def get_many_message_files(self, *args, db_query: Optional[Select] = None) -> list[MessageFile]:
        return await self.db_repository.get_many(*args, db_query=db_query)

    async def create_object_file(self, file: UploadFile, **kwargs) -> MessageFile:
        return await self.files_service.create_object_file(file, **kwargs)

    async def change_message_file(
        self,
        replacement_file: UploadFile,
        message_file: Union[MessageFile, int],
    ) -> MessageFile:
        message_file_id = self._get_message_file_id(message_file)
        new_message_file: MessageFile = await self.files_service.change_file(message_file_id, replacement_file)
        message = getattr(message_file, 'message', None)
        if message:
            await message_updated_event(self.event_publisher, message)
        return new_message_file

    async def delete_message_file(self, message_file: Optional[Union[MessageFile, int]]):
        message_file_id = self._get_message_file_id(message_file)
        await self.files_service.delete_file_object(message_file_id)
        message = getattr(message_file, 'message', None)
        if message:
            await message_updated_event(self.event_publisher, message)

    async def change_scheduled_message_file(
        self,
        replacement_file: UploadFile,
        message_file: Union[MessageFile, int],
    ) -> MessageFile:
        message_file_id = self._get_message_file_id(message_file)
        new_message_file: MessageFile = await self.files_service.change_file(message_file_id, replacement_file)
        return new_message_file

    async def delete_scheduled_message_file(self, message_file: Optional[Union[MessageFile, int]]):
        message_file_id = self._get_message_file_id(message_file)
        await self.files_service.delete_file_object(message_file_id)

    async def delete_message_files_from_filesystem(self, *args):
        file_paths = await self.db_repository.get_many(
            db_query=select(MessageFile.file_path).join(Message).where(*args),
        )
        for file_path in file_paths:
            await self.files_service.remove_file_from_filesystem(file_path)

    def _get_message_file_id(self, message_file: Optional[Union[MessageFile, int]]) -> int:
        if message_file:
            return message_file.id if isinstance(message_file, MessageFile) else message_file

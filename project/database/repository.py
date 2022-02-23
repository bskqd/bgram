from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import TypeVar, Type, Any, Optional, List, cast, AsyncContextManager

from sqlalchemy import select, update, func, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction
from sqlalchemy.sql import Select

Model = TypeVar('Model')
TransactionContext = AsyncContextManager[AsyncSessionTransaction]


class BaseTransactionRepository(ABC):
    @abstractmethod
    async def transaction(self):
        pass


class SQLAlchemyTransactionRepository(BaseTransactionRepository):
    def __init__(self, db_session: AsyncSession):
        self.__db_session = db_session

    @asynccontextmanager
    async def transaction(self) -> TransactionContext:
        async with self.__db_session as transaction:
            yield transaction
        await transaction.rollback()


class BaseCRUDRepository(ABC):
    @abstractmethod
    def add(self, object_to_add) -> None:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def refresh(self, object_to_refresh) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def create(self, **kwargs):
        pass

    @abstractmethod
    async def bulk_create(self, *args) -> None:
        pass

    @abstractmethod
    async def update_object(self, object_to_update, **kwargs):
        pass

    @abstractmethod
    async def update(self, *args: Any, **kwargs: Any):
        pass

    @abstractmethod
    async def delete(self, *args: Any):
        pass

    @abstractmethod
    async def get_one(self, *args):
        pass

    @abstractmethod
    async def get_many(self, *args):
        pass

    @abstractmethod
    async def exists(self, *args):
        pass

    @abstractmethod
    async def count(self, *args):
        pass


class SQLAlchemyCRUDRepository(BaseCRUDRepository):

    def __init__(self, model: Type[Model], db_session: AsyncSession, db_query: Optional[Select] = None):
        self.model = model
        self.__db_session = db_session
        self.db_query = db_query

    def add(self, object_to_add: Model) -> None:
        self.__db_session.add(object_to_add)

    async def commit(self) -> None:
        await self.__db_session.commit()

    async def refresh(self, object_to_refresh: Model) -> None:
        await self.__db_session.refresh(object_to_refresh)

    async def rollback(self) -> None:
        await self.__db_session.rollback()

    async def create(self, object_to_create: Optional[Model] = None, **kwargs: Any) -> Model:
        object_to_create = object_to_create if object_to_create else self.model(**kwargs)
        self.add(object_to_create)
        return object_to_create

    async def bulk_create(self, *instances) -> None:
        return await self.__db_session.bulk_save_objects(*instances)

    async def update_object(self, object_to_update: Optional[Model], **kwargs) -> Model:
        for attr, value in kwargs.items():
            setattr(object_to_update, attr, value)
        self.add(object_to_update)
        return object_to_update

    async def update(self, *args: Any, **kwargs: Any) -> Model:
        update_query = update(self.model).where(*args).values(**kwargs).returning(self.model)
        select_query = select(self.model).from_statement(update_query).execution_options(synchronize_session='fetch')
        return await self.__db_session.scalar(select_query)

    async def delete(self, *args: Any) -> List[Model]:
        db_query = delete(self.model).where(*args).returning('*')
        results = await self.__db_session.scalars(db_query)
        return results.all()

    async def get_one(self, *args) -> Model:
        return await self.__db_session.scalar(self._get_db_query(*args))

    async def get_many(self, *args: Any, unique_results: bool = True) -> Model:
        results = await self.__db_session.scalars(self._get_db_query(*args))
        return results.unique().all() if unique_results else results.all()

    async def exists(self, *args: Any) -> Optional[bool]:
        select_db_query = self._get_db_query(*args)
        exists_db_query = exists(select_db_query).select()
        result = await self.__db_session.scalar(exists_db_query)
        return cast(Optional[bool], result)

    async def count(self, *args) -> int:
        db_query = self._get_db_query(*args)
        db_query = select(func.count()).select_from(db_query)
        result = await self.__db_session.execute(db_query)
        count = result.scalar_one()
        return cast(int, count)

    def _get_db_query(self, *args):
        return self.db_query.where(*args) if self.db_query is not None else select(self.model).where(*args)

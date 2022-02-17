from contextlib import asynccontextmanager
from typing import TypeVar, Type, Any, Optional, List, cast, AsyncContextManager

from sqlalchemy import select, update, func, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction
from sqlalchemy.sql import Select

Model = TypeVar('Model')
TransactionContext = AsyncContextManager[AsyncSessionTransaction]


class SQLAlchemyTransactionRepository:
    def __init__(self, db_session: AsyncSession):
        self.__db_session = db_session

    @asynccontextmanager
    async def transaction(self) -> TransactionContext:
        async with self.__db_session as transaction:
            yield transaction
        await transaction.rollback()


class SQLAlchemyCRUDRepository:

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
        object_to_create = object_to_create if object_to_create else self._convert_to_model(**kwargs)
        self.add(object_to_create)
        return object_to_create

    async def bulk_create(self, *instances) -> None:
        return await self.__db_session.bulk_save_objects(*instances)

    async def get_one(self, *args) -> Model:
        db_query = self.db_query or select(self.model)
        db_query = db_query.where(*args)
        return await self.__db_session.scalar(db_query)

    async def get_many(self, unique_results: bool = True, *args: Any) -> Model:
        db_query = self.db_query or select(self.model)
        db_query = db_query.where(*args)
        results = await self.__db_session.scalars(db_query)
        return results.unique().all() if unique_results else results.all()

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

    async def exists(self, *args: Any) -> Optional[bool]:
        """Check is row exists in database"""
        select_db_query = self.db_query or select(self.model)
        select_db_query = select_db_query.where(*args)
        exists_db_query = exists(select_db_query).select()
        result = await self.__db_session.scalar(exists_db_query)
        return cast(Optional[bool], result)

    async def count(self, *args) -> int:
        db_query = self.db_query or select(self.model)
        db_query = db_query.where(*args)
        db_query = select(func.count()).select_from(db_query).subquery()
        result = await self.__db_session.execute(db_query)
        count = result.scalar_one()
        return cast(int, count)

    def _convert_to_model(self, **kwargs) -> Model:
        return self.model(**kwargs)

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Type, TypeVar, cast

from sqlalchemy import column, delete, exists, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from sqlalchemy.sql import Select

Model = TypeVar('Model')


class BaseDatabaseRepository(ABC):
    @abstractmethod
    def add(self, object_to_add) -> None:
        pass

    @abstractmethod
    async def flush(self):
        await self.__db_session.flush()

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
    async def create_from_object(self, *args, **kwargs):
        pass

    @abstractmethod
    async def create(self, *args, **kwargs):
        pass

    @abstractmethod
    async def update_object(self, object_to_update, **kwargs):
        pass

    @abstractmethod
    async def update(self, *args, **kwargs):
        pass

    @abstractmethod
    async def delete(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_one(self, *args, db_query: Optional[Any] = None, fields_to_load: Optional[tuple[str]] = None):
        pass

    @abstractmethod
    async def get_many(self, *args, db_query: Optional[Any] = None, fields_to_load: Optional[tuple[str]] = None):
        pass

    @abstractmethod
    async def exists(self, *args, db_query: Optional[Any] = None):
        pass

    @abstractmethod
    async def count(self, *args, db_query: Optional[Any] = None):
        pass


class SQLAlchemyDatabaseRepository(BaseDatabaseRepository):
    def __init__(self, model: Type[Model], db_session: AsyncSession):
        self.model = model
        self.__db_session = db_session

    def add(self, object_to_add: Model) -> None:
        self.__db_session.add(object_to_add)

    async def flush(self):
        await self.__db_session.flush()

    async def commit(self):
        await self.__db_session.commit()

    async def refresh(self, object_to_refresh: Model) -> None:
        await self.__db_session.refresh(object_to_refresh)

    async def rollback(self):
        await self.__db_session.rollback()

    async def create_from_object(self, object_to_create: Optional[Model] = None, **kwargs: Any) -> Model:
        object_to_create = object_to_create if object_to_create else self.model(**kwargs)
        self.add(object_to_create)
        return object_to_create

    async def create(self, _returning_options: Optional[tuple] = None, **kwargs: Any) -> Model:
        create_query = insert(self.model).values(**kwargs).returning(self.model)
        select_query = select(self.model).from_statement(create_query).execution_options(synchronize_session='fetch')
        if _returning_options:
            select_query = select_query.options(*_returning_options)
        return await self.__db_session.scalar(select_query)

    async def update_object(self, object_to_update: Model, **kwargs) -> Model:
        for attr, value in kwargs.items():
            setattr(object_to_update, attr, value)
        self.add(object_to_update)
        return object_to_update

    async def update(self, *args: Any, _returning_options: Optional[tuple] = None, **kwargs: Any) -> Model:
        update_query = update(self.model).where(*args).values(**kwargs).returning(self.model)
        select_query = select(self.model).from_statement(update_query).execution_options(synchronize_session='fetch')
        if _returning_options:
            select_query = select_query.options(*_returning_options)
        return await self.__db_session.scalar(select_query)

    async def delete(
        self,
        *args: Any,
        _returning_fields: Optional[tuple[str]] = None,
    ) -> Optional[List[Model]]:
        delete_query = delete(self.model).where(*args)
        if _returning_fields:
            if 'id' not in _returning_fields:
                _returning_fields += ('id',)
            _returning_fields = tuple(map(column, _returning_fields))
            delete_query = delete_query.returning(*_returning_fields)
            select_query = (
                select(self.model).from_statement(delete_query).execution_options(synchronize_session='fetch')
            )
            results = await self.__db_session.scalars(select_query)
            return results.all()
        await self.__db_session.execute(delete_query)

    async def get_one(
        self,
        *args,
        db_query: Optional[Select] = None,
        fields_to_load: Optional[tuple[str]] = None,
    ) -> Model:
        select_query = self._get_db_query(*args, db_query=db_query)
        if fields_to_load:
            select_query = select_query.options(load_only(*fields_to_load))
        return await self.__db_session.scalar(select_query)

    async def get_many(
        self,
        *args: Any,
        unique_results: bool = True,
        db_query: Optional[Select] = None,
        fields_to_load: Optional[tuple[str]] = None,
    ) -> Model:
        select_query = self._get_db_query(*args, db_query=db_query)
        if fields_to_load:
            select_query = select_query.options(load_only(*fields_to_load))
        results = await self.__db_session.scalars(select_query)
        return results.unique().all() if unique_results else results.all()

    async def exists(self, *args: Any, db_query: Optional[Select] = None) -> Optional[bool]:
        select_db_query = self._get_db_query(*args, db_query=db_query)
        exists_db_query = exists(select_db_query).select()
        result = await self.__db_session.scalar(exists_db_query)
        return cast(Optional[bool], result)

    async def count(self, *args, db_query: Optional[Select] = None) -> int:
        db_query = self._get_db_query(*args, db_query=db_query)
        db_query = db_query.with_only_columns([func.count()]).order_by(None)
        return await self.__db_session.scalar(db_query) or 0

    def _get_db_query(self, *args, db_query: Optional[Select]) -> Select:
        return db_query.where(*args) if db_query is not None else select(self.model).where(*args)

from abc import ABC
from typing import Optional

from fastapi import Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from accounts.models import User
from core.database.repository import BaseDatabaseRepository


class AbstractView(ABC):
    """
    Abstract class for views that support CRUD operations.
    """
    request: Request = Depends()
    request_user: Optional[User] = Depends()
    db_session: AsyncSession = Depends()
    db_query = None
    pagination_class = None
    filterset_class = None

    def get_db_query(self, *args) -> Select:
        if self.db_query is not None:
            return self.db_query
        raise HTTPException(status_code=400, detail=f'Default db query for {self.__class__} is not specified')

    def filter_db_query(self, db_query: Select) -> Select:
        if self.filterset_class:
            return self.filterset_class(db_query=db_query, request=self.request).filter_db_query()
        raise HTTPException(status_code=400, detail=f'Filterset class for {self.__class__} is not specified')

    async def get_paginated_response(
            self,
            db_repository: BaseDatabaseRepository,
            db_query: Select,
            **kwargs
    ) -> dict:
        if self.pagination_class:
            return await self.pagination_class(
                self.request,
                db_repository,
                **kwargs
            ).paginate(db_query)
        raise HTTPException(status_code=400, detail=f'Pagination class for {self.__class__} is not specified')

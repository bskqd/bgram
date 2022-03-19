from abc import ABC
from typing import Optional

from fastapi import Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from accounts.models import User
from database.repository import BaseCRUDRepository
from mixins import dependencies as mixins_dependencies


class AbstractView(ABC):
    """
    Abstract class for views that support CRUD operations.
    """
    request: Request = Depends(mixins_dependencies.get_request)
    request_user: Optional[User] = Depends(mixins_dependencies.get_request_user)
    db_session: AsyncSession = Depends(mixins_dependencies.db_session)
    db_query = None
    pagination_class = None

    def get_db_query(self, *args) -> Select:
        if self.db_query is not None:
            return self.db_query
        raise HTTPException(status_code=400, detail=f'Default db query for {self.__class__} is not specified')

    async def get_paginated_response(
            self,
            db_repository: BaseCRUDRepository,
            db_query: Select,
            **kwargs
    ) -> dict:
        pagintion_class = self.pagination_class
        if pagintion_class:
            return await pagintion_class(
                self.request,
                db_repository,
                **kwargs
            ).paginate(db_query)
        raise HTTPException(status_code=400, detail=f'Pagination class for {self.__class__} is not specified')

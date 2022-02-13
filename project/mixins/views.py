from abc import ABC
from typing import List, Optional

from fastapi import Request, Depends, HTTPException
from sqlalchemy.sql import Select

from accounts.models import User
from database.base import Base
from mixins import dependencies as mixins_dependencies


class AbstractView(ABC):
    """
    Abstract class for views that support CRUD operations.
    """
    request: Request = Depends(mixins_dependencies.get_request)
    request_user: Optional[User] = Depends(mixins_dependencies.get_request_user)
    db_query = None
    pagination_class = None

    def get_db_query(self, *args) -> Select:
        if hasattr(self, 'db_query'):
            return self.db_query
        raise HTTPException(status_code=400, detail=f'Default db query for {self.__class__} is not specified')

    def get_paginated_response(self, queryset: List[Base], **kwargs) -> dict:
        pagintion_class = self.pagination_class
        if pagintion_class:
            return pagintion_class(self.request, **kwargs).paginate(queryset)
        raise HTTPException(status_code=400, detail=f'Pagination class for {self.__class__} is not specified')

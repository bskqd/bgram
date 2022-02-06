from abc import ABC, abstractmethod
from typing import List, Optional

from fastapi import Request, Depends, HTTPException
from sqlalchemy.sql import Select

from accounts.models import User
from database import Base
from mixins import dependencies as mixins_dependencies


class AbstractView(ABC):
    """
    Abstract class for views that support CRUD operations.
    """
    request: Request = Depends(mixins_dependencies.get_request)
    request_user: Optional[User] = Depends(mixins_dependencies.get_request_user)
    pagination_class = None

    @property
    @abstractmethod
    def queryset(self) -> Select:
        """
        Must return queryset available for exact request.
        """
        pass

    def get_paginated_response(self, queryset: List[Base], **kwargs) -> dict:
        pagintion_class = self.pagination_class
        if not pagintion_class:
            raise HTTPException(status_code=400, detail=f'Pagination class for {self.__class__} is not specified')
        return pagintion_class(self.request, **kwargs).paginate(queryset)

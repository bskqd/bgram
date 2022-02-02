from abc import ABC, abstractmethod

from fastapi import Request, Depends
from sqlalchemy.sql import Select

from mixins import dependencies as mixins_dependencies


class AbstractView(ABC):
    """
    Abstract class for views that support CRUD operations.
    """
    request: Request = Depends(mixins_dependencies.get_request)

    @property
    @abstractmethod
    def queryset(self) -> Select:
        """
        Must return queryset available for exact request.
        """
        pass

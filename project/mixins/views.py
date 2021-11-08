from abc import ABC, abstractmethod

from sqlalchemy.engine import ChunkedIteratorResult


class AbstractView(ABC):
    """
    Abstract class for views that support CRUD operations.
    """

    @property
    @abstractmethod
    def available_db_data(self) -> ChunkedIteratorResult:
        """
        Must return queryset available for exact request.
        """
        pass

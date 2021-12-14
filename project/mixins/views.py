from abc import ABC, abstractmethod

from sqlalchemy.sql import Select


class AbstractView(ABC):
    """
    Abstract class for views that support CRUD operations.
    """

    @property
    @abstractmethod
    def available_db_data(self) -> Select:
        """
        Must return queryset available for exact request.
        """
        pass

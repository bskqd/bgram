from sqlalchemy import Column, DateTime, func, String, Integer, Boolean

from database import Base


class DateTimeABC(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=func.now())
    modified_at = Column(DateTime, default=func.now(), onupdate=func.now())


class DescriptionABC(Base):
    __abstract__ = True

    description = Column(String, default='')


class IsActiveABC(Base):
    __abstract__ = True

    is_active = Column(Boolean, default=True)


class Photo(DateTimeABC):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    file_path = Column(String, unique=True)

    @property
    def folder_to_save(self) -> str:
        """
        Must return path to directory where to save a file.
        """
        raise NotImplementedError()

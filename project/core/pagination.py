import math
from abc import ABC
from typing import Tuple

from fastapi import Request
from sqlalchemy.sql import Select

from core.database.base import Base


class PaginationDatabaseObjectsRetrieverStrategyABC(ABC):
    async def get_many(self, db_query: Select) -> list[Base]:
        pass

    async def count(self, db_query: Select) -> int:
        pass


class DefaultPaginationClass:
    def __init__(
            self,
            request: Request,
            db_objects_retriever_strategy: PaginationDatabaseObjectsRetrieverStrategyABC,
            page_number_param: str = 'page',
            page_size_param: str = 'page_size',
    ):
        self.request = request
        self.request_query_params = request.query_params
        self.page_number_param = page_number_param
        self.page_size_param = page_size_param
        self.db_objects_retriever_strategy = db_objects_retriever_strategy

    async def paginate(self, db_query: Select) -> dict:
        page_size: int = int(self.request_query_params.get(self.page_size_param, 20))
        current_page_number: int = int(self.request_query_params.get(self.page_number_param, 1))
        db_query_offset = page_size * (current_page_number - 1)
        db_query_limit = page_size * current_page_number
        total_db_objects_count = await self.db_objects_retriever_strategy.count(db_query)
        db_query = db_query.offset(db_query_offset).limit(db_query_limit)
        db_objects = await self.db_objects_retriever_strategy.get_many(db_query)
        total_pages = math.ceil(total_db_objects_count / page_size)
        previous_page_url, next_page_url = self.get_previous_and_next_page_urls(
            current_page_number, db_query_limit, total_db_objects_count
        )
        return {
            'data': db_objects,
            'count': total_db_objects_count,
            'total_pages': total_pages,
            'current_page': current_page_number,
            'page_size': page_size,
            'next': next_page_url,
            'previous': previous_page_url,
        }

    def get_previous_and_next_page_urls(
            self,
            current_page_number: int,
            db_query_limit: int,
            total_db_objects_count: int,
    ) -> Tuple[str, str]:
        url = self.request.url
        url_contains_page_number_param: bool = bool(self.request_query_params.get(self.page_number_param))
        url = str(url)
        previous_page = self.get_previous_page_url(url, current_page_number, url_contains_page_number_param)
        next_page = self.get_next_page_url(
            url, current_page_number, url_contains_page_number_param, db_query_limit, total_db_objects_count
        )
        return previous_page, next_page

    def get_previous_page_url(self, url: str, current_page_number: int, url_contains_page_number_param: bool):
        if current_page_number == 1:
            return None
        elif url_contains_page_number_param:
            return url.replace(
                f'{self.page_number_param}={current_page_number}', f'{self.page_number_param}={current_page_number - 1}'
            )
        elif self.request_query_params:
            return f'{url}&{self.page_number_param}={current_page_number - 1}'
        return f'{url}?{self.page_number_param}={current_page_number - 1}'

    def get_next_page_url(
            self,
            url: str,
            current_page_number: int,
            url_contains_page_number_param: bool,
            db_query_limit: int,
            total_db_objects_count: int,
    ):
        if db_query_limit >= total_db_objects_count:
            return None
        elif url_contains_page_number_param:
            return url.replace(
                f'{self.page_number_param}={current_page_number}', f'{self.page_number_param}={current_page_number + 1}'
            )
        elif self.request_query_params:
            return f'{url}&{self.page_number_param}={current_page_number + 1}'
        return f'{url}?{self.page_number_param}={current_page_number + 1}'

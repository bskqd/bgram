from collections import OrderedDict
from typing import Type, Optional

from fastapi import Request, HTTPException
from sqlalchemy.sql import Select

from core.database.base import Base
from core.filters.filters import BaseFilter

__all__ = ['FilterSetMetaclass', 'BaseFilterSet', 'FilterSet']


# TODO: it's not necessary to instantiate a filterset on every request (view dependencies)
class FilterSetMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['filters'] = cls.get_filters(bases, attrs)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def get_filters(cls, bases, attrs):
        model_class = attrs.get('model_class')
        if not model_class and not (len(bases) == 1 and bases[0] == BaseFilterSet):
            raise AttributeError('FilterSet must declare model_class attribute')

        filters = {
            filter_name: cls.modify_filter_attributes(
                filter_instance=filter_instance, filter_name=filter_name, model_class=model_class,
            )
            for filter_name, filter_instance in list(attrs.items())
            if isinstance(filter_instance, BaseFilter)
        }

        # Ensures a base class field doesn't override cls attrs,
        # and maintains field precedence when inheriting multiple parents. e.g. if there is a class C(A, B),
        # and A and B both define 'field', use 'field' from A.
        known = set(filters)

        def visit(name):
            known.add(name)
            return name

        base_filters = {
            visit(filter_name): cls.modify_filter_attributes(
                filter_instance=filter_instance, filter_name=filter_name, model_class=model_class,
            )
            for base in bases if hasattr(base, 'filters')
            for filter_name, filter_instance in base.filters.items() if filter_name not in known
        }
        filters.update(base_filters)

        return OrderedDict(filters)

    @classmethod
    def modify_filter_attributes(
            cls,
            filter_instance: BaseFilter,
            filter_name: str,
            model_class: Type[Base],
    ) -> BaseFilter:
        setattr(filter_instance, 'name', filter_name)
        if not filter_instance.model_class:
            setattr(filter_instance, 'model_class', model_class)
        return filter_instance


class BaseFilterSet:
    filters: dict

    def __init__(self, request: Request):
        self.request = request
        self.query_params = request.query_params

    def filter_db_query(self, db_query: Select):
        for query_param_name, query_param_value in self.query_params.items():
            filter_instance: Optional[BaseFilter] = self.filters.get(query_param_name)
            if not filter_instance:
                continue
            if filter_instance.method_name:
                db_query = self.filter_db_query_by_method(db_query, filter_instance, query_param_value)
                continue
            db_query = filter_instance.filter(db_query, query_param_value)
        return db_query

    def filter_db_query_by_method(self, db_query: Select, filter_instance: BaseFilter, value: str) -> Select:
        method = getattr(self, filter_instance.method_name, None)
        if method is None:
            raise HTTPException(
                status_code=500,
                detail=f'{filter_instance.__class__.__name__} does not have {filter_instance.method_name} method',
            )
        value = filter_instance.validate_value(value)
        return method(db_query, value)


class FilterSet(BaseFilterSet, metaclass=FilterSetMetaclass):
    pass

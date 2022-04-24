import operator
from typing import Optional, Callable, Any

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import Select

from database.base import Base

__all__ = [
    'BaseFilter', 'IntegerFilter', 'CharFilter', 'like', 'ilike', 'contains', 'icontains',
]


def like(model_field: InstrumentedAttribute, value: Any):
    return model_field.like(value)


def ilike(model_field: InstrumentedAttribute, value: Any):
    return model_field.ilike(value)


def contains(model_field: InstrumentedAttribute, value: Any):
    return model_field.contains(value)


def icontains(model_field: InstrumentedAttribute, value: Any):
    return func.lower(model_field).contains(func.lower(value))


LOOKUP_EXPR_MAPPER: dict[str, Callable] = {
    '==': operator.eq,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
    'like': like,
    'ilike': ilike,
    'contains': contains,
    'icontains': icontains,
}


class BaseFilter:
    def __init__(
            self,
            model_class: Optional[Base] = None,
            field_name: Optional[str] = None,
            lookup_expr: str = '==',
            method_name: Optional[str] = None,
    ):
        self.name = ''
        self.model_class = model_class
        self.field_name = field_name
        self.lookup_expr = LOOKUP_EXPR_MAPPER.get(lookup_expr)
        self.method_name = method_name

    def filter(self, db_query: Select, value: str) -> Select:
        value = self.validate_value(value)
        return db_query.where(self.lookup_expr(getattr(self.model_class, self.field_name), value))

    def validate_value(self, value: str) -> str:
        return value


class IntegerFilter(BaseFilter):
    def validate_value(self, value: str) -> int:
        return int(value)


class CharFilter(BaseFilter):
    def __init__(
            self,
            model_class: Optional[Base] = None,
            field_name: Optional[str] = None,
            lookup_expr: str = '==',
            method_name: Optional[str] = None,
            min_length: Optional[int] = None,
            max_length: Optional[int] = None,
    ):
        super().__init__(
            model_class=model_class, field_name=field_name, lookup_expr=lookup_expr, method_name=method_name
        )
        self.min_length = min_length
        self.max_length = max_length

    def validate_value(self, value: str) -> str:
        value_length = len(value)
        if self.min_length and value_length < self.min_length:
            raise HTTPException(status_code=400, detail=f'{self.name} value is too short')
        if self.max_length and value_length > self.max_length:
            raise HTTPException(status_code=400, detail=f'{self.name} value is too long')
        return value

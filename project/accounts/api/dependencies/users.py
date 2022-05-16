from fastapi import Request

from accounts.api.v1.filters.users import UsersFilterSet
from core.filters import FilterSet


async def get_users_filterset(request: Request) -> FilterSet:
    return UsersFilterSet(request=request)

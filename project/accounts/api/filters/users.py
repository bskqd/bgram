from accounts.models import User
from core.filters import CharFilter, FilterSet, icontains
from sqlalchemy import or_
from sqlalchemy.sql import Select


class UserFilterSetABC(FilterSet):
    model_class = User


class UsersFilterSet(UserFilterSetABC):
    model_class = User
    search = CharFilter(min_length=3, method_name='universal_search')

    def universal_search(self, db_query: Select, value: str) -> Select:
        return db_query.where(or_(icontains(User.nickname, value), icontains(User.email, value)))

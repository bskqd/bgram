from sqlalchemy.sql import Select

from accounts.models import User
from mixins.filters import CharFilter, FilterSet, icontains
from sqlalchemy import or_


class UsersFilterSet(FilterSet):
    model_class = User
    search = CharFilter(min_length=3, method_name='universal_search')

    def universal_search(self, db_query: Select, value: str) -> Select:
        return db_query.where(or_(icontains(User.nickname, value), icontains(User.email, value)))

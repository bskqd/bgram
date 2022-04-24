from sqlalchemy import or_
from sqlalchemy.sql import Select

from accounts.models import User
from chat.models import Message
from core.filters import CharFilter, FilterSet, icontains


class MessagesFilterSet(FilterSet):
    model_class = Message
    search = CharFilter(min_length=3, method_name='universal_search')

    def universal_search(self, db_query: Select, value: str) -> Select:
        return db_query.join(Message.author).where(
            or_(icontains(Message.text, value), icontains(User.nickname, value))
        )

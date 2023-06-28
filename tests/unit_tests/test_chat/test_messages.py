import pytest
from chat.constants.messages import MessagesTypeEnum
from chat.database.selectors.messages import get_message_creation_relations_to_load
from chat.services.messages import MessagesCreateUpdateDeleteServiceABC


@pytest.mark.asyncio
async def test_create_primary_message(messages_create_update_delete_service: MessagesCreateUpdateDeleteServiceABC):
    message = await messages_create_update_delete_service.create_message(
        text='test message text',
        relations_to_load_after_creation=get_message_creation_relations_to_load(),
    )
    assert message.text == 'test message text'
    assert message.message_type == MessagesTypeEnum.PRIMARY


@pytest.mark.asyncio
async def test_create_scheduled_message(messages_create_update_delete_service: MessagesCreateUpdateDeleteServiceABC):
    message = await messages_create_update_delete_service.create_scheduled_message(text='test message text')
    assert message.text == 'test message text'
    assert message.message_type == MessagesTypeEnum.SCHEDULED
    assert message.scheduler_task_id


@pytest.mark.asyncio
async def test_fail():
    raise Exception('ABOBA')

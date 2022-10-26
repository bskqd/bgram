import pytest

from chat.services.messages import MessagesCreateUpdateDeleteServiceABC


@pytest.mark.asyncio
async def test_create_message(messages_create_update_delete_service: MessagesCreateUpdateDeleteServiceABC):
    message = await messages_create_update_delete_service.create_message(text='test message text')
    assert message.text == 'test message text'

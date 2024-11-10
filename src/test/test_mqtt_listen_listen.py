"""Mqtt_listen execute tests."""

import asyncio
import logging
from unittest import mock
import pytest
from mqtt_listen.listen import setup_client, QueueOnMessageFactory

_log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_setup_client():
    """Test setup_client."""
    m_broker = "broker"
    m_topic = "test/test_setup_client"

    class AsyncForMock:
        def __init__(self, messages):
            self._messages = messages

        def __aiter__(self):
            return self

        async def __anext__(self):
            if not self._messages:
                raise StopAsyncIteration
            return self._messages.pop(0)

    # Mock the aiomqtt.Client() async context manager
    with mock.patch("mqtt_listen.listen.aiomqtt.Client", autospec=True) as m_client:
        # Mock the client instance
        m_client_instance = m_client.return_value.__aenter__.return_value
        m_client_instance.messages = AsyncForMock([mock.Mock()])

        # Mock the on_message function
        on_message = mock.AsyncMock()

        # Run the setup_client function
        setup_task = asyncio.create_task(setup_client(m_broker, m_topic, on_message))

        # Allow some time for the task to run
        await asyncio.sleep(0.1)

        # Cancel the task to stop the infinite loop
        setup_task.cancel()
        try:
            await setup_task
        except asyncio.CancelledError:
            pass

        # Assert the client was created with the correct hostname
        m_client.assert_called_once_with(m_broker)
        # Assert the client was subscribed to the correct topic
        m_client_instance.subscribe.assert_called_once_with(m_topic)
        # Assert the on_message function was called with the message
        on_message.assert_called_once()


@pytest.mark.asyncio
async def test_queue_on_message_factory():
    """Test QueueOnMessageFactory."""
    m_queue = asyncio.Queue()
    m_msg = mock.Mock()
    m_msg.payload = b"test_payload"
    m_msg.topic = "test/test_queue_on_message_factory"
    m_msg.qos = 0

    # Create the QueueOnMessageFactory instance
    queue_on_message_factory = QueueOnMessageFactory(m_queue)

    # Call the on_message function
    await queue_on_message_factory.__call__(m_msg)

    # Assert the message was added to the queue
    assert m_queue.qsize() == 1
    assert m_queue.get_nowait() == m_msg
    assert m_queue.empty() is True
    assert queue_on_message_factory.queue == m_queue

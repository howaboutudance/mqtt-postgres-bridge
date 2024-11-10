"""Integration test mqtt_listen."""

import asyncio
import logging
import re

import aiomqtt
import pytest

from mqtt_listen.config import CONFIG
from mqtt_listen.listen import setup_client

# Mark this test module as containing integration tests
pytestmark = [pytest.mark.integration]

# Logger
_log = logging.getLogger(__name__)


async def _publish_messages(broker: str, topic: str):
    async with aiomqtt.Client(broker) as client:
        for i in range(5):
            await client.publish(topic, f"test {i}")
            asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_intg_setup_client():
    """Integration test for setup_client."""
    m_broker = CONFIG.get("mqtt_broker.hostname")
    m_topic = "test/test_intg_setup_client"

    async def on_message(msg: aiomqtt.Message):
        # Assert the message is an instance of aiomqtt.Message
        assert isinstance(msg, aiomqtt.Message)

        # Assert the payload is a string and matches the pattern
        payload_resp = msg.payload.decode()
        assert "test" in payload_resp
        assert re.match(r"test \d", payload_resp)

        # Assert the topic and qos
        assert msg.topic == m_topic
        assert msg.qos == 0

    # Create a task to listen for message and one to publish messages
    # to the broker, sleep for a second and then cancel the listen task
    test_task = asyncio.create_task(setup_client(m_broker, m_topic, on_message))
    await asyncio.create_task(_publish_messages(m_broker, m_topic))

    await asyncio.sleep(1)

    # caneel the task
    test_task.cancel()

    try:
        await test_task
    except asyncio.CancelledError:
        pytest.success("Task was cancelled successfully")

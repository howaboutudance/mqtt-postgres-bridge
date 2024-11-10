"""Test the mqtt_listen.processor module"""

import asyncio
from unittest.mock import AsyncMock

import aiomqtt
import pytest

from mqtt_listen.process import (process_messages_to_log,
                                 process_messages_to_queue)


@pytest.mark.parametrize("queue_content, mocked_queue", [([], False), ([1, 2, 3], False), (None, True)])
@pytest.mark.asyncio
async def test_process_messages_to_log(queue_content, mocked_queue):
    m_topic = "test/test_process_messages_to_log"
    m_qos = 0
    if mocked_queue:
        m_input_queue = AsyncMock(spec=asyncio.Queue)
        m_input_queue.empty.return_value = False
    else:
        m_input_queue = asyncio.Queue()
        [
            await m_input_queue.put(
                aiomqtt.Message(topic=m_topic, qos=m_qos, payload=str(i).encode(), retain=False, mid=0, properties=None)
            )
            for i in queue_content
        ]

    process_task = asyncio.create_task(process_messages_to_log(m_input_queue))

    await asyncio.sleep(0.1)
    process_task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await process_task

    if mocked_queue:
        m_input_queue.get.assert_called()
        m_input_queue.empty.assert_called()


# test the proccess_messages_to_queue function
@pytest.mark.parametrize("queue_content, mocked_queue", [([], False), ([1, 2, 3], False), (None, True)])
@pytest.mark.asyncio
async def test_process_messages_to_queue(queue_content, mocked_queue):
    m_topic = "test/test_process_messages_to_queue"
    m_qos = 0
    if mocked_queue:
        m_input_queue = AsyncMock(spec=asyncio.Queue)
        m_input_queue.empty.return_value = False
    else:
        m_input_queue = asyncio.Queue()
        [
            await m_input_queue.put(
                aiomqtt.Message(topic=m_topic, qos=m_qos, payload=str(i).encode(), retain=False, mid=0, properties=None)
            )
            for i in queue_content
        ]

    m_output_queue = asyncio.Queue()
    process_task = asyncio.create_task(process_messages_to_queue(m_input_queue, m_output_queue))

    await asyncio.sleep(0.1)
    process_task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await process_task

    if mocked_queue:
        m_input_queue.get.assert_called()
        m_input_queue.empty.assert_called()
    else:
        assert m_output_queue.qsize() == len(queue_content)
        for i in queue_content:
            message = await m_output_queue.get()
            assert str(message.topic) == m_topic
            assert message.qos == m_qos
            assert int(message.payload.decode()) == i

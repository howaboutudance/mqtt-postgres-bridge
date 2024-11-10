"""Test the mqtt_listen.processor module."""

import asyncio
from unittest.mock import AsyncMock

import aiomqtt
import pytest

from mqtt_listen.process import (process_messages_to_log,
                                 process_messages_to_queue)


@pytest.mark.parametrize("queue_content, mocked_queue", [([], False), ([1, 2, 3], False), (None, True)])
@pytest.mark.asyncio
async def test_process_messages_to_log(queue_content, mocked_queue):
    """Test the process_messages_to_log function.

    Test Plan:
    - parametrize the test with empty queue, queue with 3 messages and mocked queue
    - create an input queue with the given content
    - create a task with the process_messages_to_log function
    - wait for 0.1 seconds
    - cancel the task
    - check if the task was cancelled
    - if mocked queue, check if the get and empty methods were called
    """
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
    """Test the process_messages_to_queue function.

    Test Plan:
    - parametrize the test with empty queue, queue with 3 messages and mocked queue
    - create an input queue with the given content
    - create a task with the process_messages_to_queue function, wait and cancel it
    - either:
        - assert that methods were called on the mocked queue
        - assert the output queue has the same content as the input queue
    """
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

import asyncio

import pytest

from psycopg_async_notify.db import get_cursor
from psycopg_async_notify.execute import listen_for_notifications
from psycopg_async_notify.publish import help_send_notification


@pytest.mark.integration
@pytest.mark.asyncio
async def test_intg_listen_for_notifications():
    # write an integration test that uses two client connections to:
    # 1. listen for notifications that are added to a queue
    # 2. execute a notification
    # 3. assert the notification sent is in the queue

    # create a queue to hold the notifications
    m_queue = asyncio.Queue()

    m_channel = "test_channel"
    m_payload = "test_payload"

    # create a task to listen for notifications, timeout if after 5 seconds
    listen_task = asyncio.create_task(listen_for_notifications(m_channel, m_queue))

    async def run_test_task(queue, listening_task):
        try:
            # wait for the listening task to start listening
            await asyncio.sleep(0.1)

            # send a notification
            await help_send_notification(m_channel, m_payload)

            # wait for the notification to be added to the queue
            await asyncio.sleep(0.1)

            result = await asyncio.wait_for(queue.get(), timeout=1)
            assert result == m_payload

        finally:
            # cancel the listening task
            listening_task.cancel()
            await listening_task

    # run the test task but timeout after 5 seconds
    try:
        await asyncio.wait_for(run_test_task(m_queue, listen_task), timeout=10)
    except asyncio.TimeoutError:
        assert False, "Test timed out"


# write a integration test to connect to the database
@pytest.mark.integration
@pytest.mark.asyncio
async def test_intg_cursor():
    async with get_cursor() as cursor:
        await cursor.execute("SELECT 1;")
        result = await cursor.fetchone()
        assert result == (1,)

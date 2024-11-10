"""Main logic of the application."""

import asyncio
import logging

from psycopg_async_notify.db import get_connection
from psycopg_async_notify.listen import QueuePutNotifyHandler

_log = logging.getLogger(__name__)


async def listen_for_notifications(channel: str, queue: asyncio.Queue):
    """Listen for notifications on a channel and add them to a queue.

    :param channel: The channel to listen for notifications on.
    :param queue: The queue to add the notifications to.
    """
    # write function that will listen to notifications on a channel and add them to a queue
    # this function will run indefinitely until:
    # 1. the task is cancelled
    # 2. the connection is closed
    # 3. an exception is raised
    notify_handler_factory = QueuePutNotifyHandler(queue)

    async with get_connection() as conn:
        await conn.execute(f"LISTEN {channel};")
        conn.add_notify_handler(notify_handler_factory.callback)

        while True:
            try:
                await conn.execute("SELECT 1;")
                await asyncio.sleep(1)
            except asyncio.CancelledError as e:
                conn.remove_notify_handler(notify_handler_factory.callback)
                await conn.execute(f"UNLISTEN {channel};")
                raise e

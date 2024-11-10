"""Functions to publish to PostgreSQL NOTIFY channel asynchronously"""

import asyncio
import json
import logging
import uuid

from psycopg_async_listen import db
from psycopg_async_listen.db import get_connection

# Logger
_log = logging.getLogger(__name__)


async def publish_to_pg_notify(queue: asyncio.Queue, topic: str):
    """Publish messages to a PostgreSQL NOTIFY channel.

    :param queue: The queue to get messages from.
    """
    # Connect asycnronously to the PostgreSQL database
    async with db.get_connection() as conn:
        async with conn.cursor() as cur:
            # Process messages from the queue
            # verify the PG NOTIFY channel exists is not, create it
            while True:
                if not queue.empty():
                    message = await queue.get()
                    json_payload = json.dumps(
                        {"topic": str(message.topic), "payload": str(message.payload.decode()), "qos": message.qos}
                    )
                    _log.debug(
                        f"func=publish_to_pg_notify json_payload={json_payload} msg_topic={message.topic} msg_qos={message.qos}"
                    )
                    await cur.execute(
                        "SELECT pg_notify (%(channel)s, %(payload)s)", {"channel": topic, "payload": json_payload}
                    )

                await asyncio.sleep(0)

    _log.info("func=publish_to_pg_notify msg=stopping")


# write a helper function that will execute the notification
# using a connection and cursor
async def help_send_notification(channel: str = "test_channel", payload: str = "test_payload"):
    async with get_connection() as conn:
        _log.debug("sending notification")
        await conn.execute("SELECT pg_notify (%(channel)s, %(payload)s)", {"channel": channel, "payload": payload})


async def help_send_notifcations_continuously(channel: str = "test_channel", payload: str = "test_payload"):
    """Send notifications continuously until keyboard interrupt."""
    async with get_connection() as conn:
        while True:
            try:
                # generate a random uuid to append to the payload
                payload_count = str(uuid.uuid4().hex)
                payload_msg = f"{payload}-{payload_count}"
                await conn.execute(
                    "SELECT pg_notify (%(channel)s, %(payload)s)", {"channel": channel, "payload": payload_msg}
                )
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                # send notify with a stop payload
                await conn.execute(
                    "SELECT pg_notify (%(channel)s, %(payload)s)", {"channel": channel, "payload": "stop"}
                )
                break

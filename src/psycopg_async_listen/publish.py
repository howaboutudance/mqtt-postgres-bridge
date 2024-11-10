"""A publisher to publish aiomqtt messages to a PostgreSQL NOTIFY channel asynchronously"""

import asyncio
import json
import logging

from psycopg_async_listen import db

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

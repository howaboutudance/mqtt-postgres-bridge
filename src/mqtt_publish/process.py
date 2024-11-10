"""Functions to process mesages from the MQTT broker to another datastore."""

import asyncio
import logging

from mqtt_listen.listen import QueueOnMessageFactory, setup_client
from mqtt_listen.process import process_messages_to_queue
from psycopg_async_notify.publish import publish_to_pg_notify

# Logger
_log = logging.getLogger(__name__)


async def publish_to_postgres(broker: str, topic: str):
    """Main function to setup the MQTT client and process messages."""
    from_mqtt_queue = asyncio.Queue()
    to_pg_notify_queue = asyncio.Queue()

    # setup three tasks:
    # - Listen to the MQTT broker and add messages to a queue
    # - Process messages from the queue and add them to another queue
    # - Publish messages from the other queue to a PostgreSQL NOTIFY channel
    client_task = asyncio.create_task(setup_client(broker, topic, QueueOnMessageFactory(from_mqtt_queue)))
    process_task = asyncio.create_task(process_messages_to_queue(from_mqtt_queue, to_pg_notify_queue))
    publish_task = asyncio.create_task(publish_to_pg_notify(to_pg_notify_queue, topic))
    await asyncio.sleep(1)

    _log.debug("starting client_task")
    await client_task
    await asyncio.sleep(1)

    _log.debug("starting process_task")
    await process_task
    await asyncio.sleep(1)

    _log.debug("starting publish_task")
    await publish_task

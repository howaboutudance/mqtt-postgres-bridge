"""A sample script demonstrating using mqtt_listen to listen to messages from an MQTT broker
and pass them to PostgreSQL NOTIFY channel."""

import asyncio
import logging

from mqtt_publish.process import publish_to_postgres

# Logger
_log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    broker_hostname = "localhost"
    topic = "test/try_publish_to_mqtt"
    try:
        asyncio.run(publish_to_postgres(broker_hostname, topic))
    except KeyboardInterrupt:
        _log.debug("closing...")
        # cancel all tasks
        for task in asyncio.all_tasks():
            task.cancel()
        exit()

"""Execute the MQTT Listerner."""

import asyncio
import logging

from mqtt_listen.config import CONFIG
from mqtt_listen.listen import QueueOnMessageFactory, setup_client
from mqtt_listen.process import process_messages_to_log

# Logger
_log = logging.getLogger(__name__)


# main function
async def listen_and_logs(broker: str, topic: str):
    """Main function to run the MQTT listener.

    :param broker: The hostname of the MQTT broker.
    :param topic: The topic to subscribe to.
    """
    msg_queue = asyncio.Queue()

    # Setup two tasks:
    # 1. Listen to the MQTT broker and add messages to a queue
    # 2. Process messages from the queue and log them
    client_task = await asyncio.create_task(setup_client(broker, topic, QueueOnMessageFactory(msg_queue)))
    process_task = await asyncio.create_task(process_messages_to_log(msg_queue))
    await asyncio.sleep(1)

    await client_task()
    await process_task()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    broker_hostname = CONFIG.get("mqtt_broker_hostname")
    topic = CONFIG.get("mqtt_topic")
    try:
        asyncio.run(listen_and_logs(broker_hostname, topic))
    except KeyboardInterrupt:
        _log.debug("closing...")
        # cancel all tasks
        for task in asyncio.all_tasks():
            task.cancel()
        exit()

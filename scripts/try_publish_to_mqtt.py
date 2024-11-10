import asyncio
import logging
import random

from aiomqtt import Client

# Setup a logger
_log = logging.getLogger(__name__)

async def publish_random_values(broker: str, topic: str):
    async with Client(broker) as client:
        while True:
            value = random.random()
            _log.debug(f"Publishing value: {value}")
            await client.publish(topic, str(value))
            await asyncio.sleep(1)  # Publish every second

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    broker = "localhost"  # Replace with your MQTT broker address
    topic = "test/try_publish_to_mqtt"
    asyncio.run(publish_random_values(broker, topic))
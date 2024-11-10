"""Listener for MQTT brokers."""

import asyncio
import logging

from abc import abstractmethod
from typing import Any, Coroutine, Protocol

import aiomqtt

# Logger
_log = logging.getLogger(__name__)


# setup client and listen
async def setup_client(hostname: str, topic: str, on_message: Coroutine[(aiomqtt.Message), Any, None]):
    """Setup the MQTT client and listen for messages.

    :param hostname: The hostname of the MQTT broker.
    :param topic: The topic to subscribe to.
    :param on_message: The function to call when a message is recieved.
    """
    async with aiomqtt.Client(hostname) as client:
        _log.debug("subscribing_to=%s server=%s", topic, hostname)
        client.subscribe(topic)

        while True:
            # if message is received, call the on_message function
            async for message in client.messages:
                await on_message(message)
            await asyncio.sleep(0)


# Creata a protocol for on_message functions
class OnMessageFactoryProtocol(Protocol):
    """Protocol for creating on_message functions."""

    @abstractmethod
    async def __call__(self, msg: aiomqtt.Message):
        """Function to call when a message is recieved.

        :param msg: The message that was recieved.
        """


class QueueOnMessageFactory(OnMessageFactoryProtocol):
    """Factory for creating on_message functions that add messages to a queue."""

    def __init__(self, queue: asyncio.Queue):
        """Initialize the factory with a queue.

        :param queue: The queue to add messages to.
        """
        self._queue = queue

    async def __call__(self, msg: aiomqtt.Message):
        """Add the message to the queue.

        :param msg: The message to add to the queue.
        """
        _log.debug(
            f"func=QueueOnMessageFactory msg_payload={msg.payload.decode()} msg_topic={msg.topic} msg_qos={msg.qos}"
        )
        await self._queue.put(msg)

    @property
    def queue(self):
        """Get the queue."""
        return self._queue

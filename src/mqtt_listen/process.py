"""Processors for Queue messages."""
import asyncio
import logging


# Logger
_log = logging.getLogger(__name__)

# process messages
async def process_messages_to_log(queue: asyncio.Queue):
    """Process messages from the queue.

    :param queue: The queue to get messages from.
    """
    while True:
        if not queue.empty():
            message = await queue.get()
            _log.debug(f"func=process_messages msg_payload={message.payload.decode()} msg_topic={message.topic} msg_qos={message.qos}")

        await asyncio.sleep(0)

# process messages into another queue
async def process_messages_to_queue(input_queue: asyncio.Queue, output_queue: asyncio.Queue):
    """Process messages from the queue to another queue.

    :param queue: The queue to get messages from.
    :param new_queue: The queue to put messages to.
    """
    while True:
        if not input_queue.empty():
            message = await input_queue.get()
            _log.debug(f"func=process_messages_to_queue msg_payload={message.payload.decode()} msg_topic={message.topic} msg_qos={message.qos}")
            await output_queue.put(message)

        await asyncio.sleep(0)
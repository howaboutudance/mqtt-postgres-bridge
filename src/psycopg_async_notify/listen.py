"""Queue handlers for psycopg async notifications."""

import asyncio
import logging

import psycopg

# logger
_log = logging.getLogger(__name__)


class QueuePutNotifyHandler:
    """Callable class to handle notifications and add them to a queue."""

    # create a callable class that will handle notifications but can configured
    # with the queue to add the notifications to
    def __init__(self, queue: asyncio.Queue):
        """Initialise the QueuePutNotifyHandler.

        :param queue: asyncio.Queue object
        """
        self.queue = queue

    def callback(self, msg: psycopg.Notify):
        """Callback to handle notifications.

        :param msg: psycopg.Notify object
        """
        _log.debug("Received notification: %s from %s", msg.payload, msg.channel)
        asyncio.run_coroutine_threadsafe(self.queue.put(msg.payload), asyncio.get_event_loop())

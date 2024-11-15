"""Tests for the psycopg_async_notify.listen module."""

import asyncio
import logging
from unittest import mock

import pytest

from psycopg_async_notify.listen import QueuePutNotifyHandler

# Logger
_log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_queue_put_notify_handler():
    """Test QueuePutNotifyHandler."""
    m_notification = "test_payload"
    m_queue = asyncio.Queue()
    m_handler = QueuePutNotifyHandler(m_queue)

    assert m_handler.queue is m_queue

    m_notify = mock.Mock()
    m_notify.payload = m_notification

    m_handler.callback(m_notify)

    assert await m_queue.get() == m_notification

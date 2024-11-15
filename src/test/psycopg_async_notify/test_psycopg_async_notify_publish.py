"""Tests for psycopg_async_notify.publish."""

import asyncio
from unittest import mock

import aiomqtt
import psycopg
import pytest

from psycopg_async_notify.publish import (help_send_notifcations_continuously,
                                          help_send_notification,
                                          publish_to_pg_notify)

pytestmark = pytest.mark.asyncio


async def test_publish_to_pg_notify():
    """Test publish_to_pg_notify."""
    m_connection = mock.AsyncMock(spec=psycopg.AsyncConnection)
    m_cursor = mock.AsyncMock(spec=psycopg.AsyncCursor)
    m_topic = "test/test_publish_to_pg_notify"

    with mock.patch("psycopg_async_notify.publish.get_connection", return_value=m_connection) as m_get_connection:
        m_aenter_m_get_connection = m_get_connection.return_value.__aenter__
        m_aenter_m_get_connection.return_value = m_connection

        m_connection.cursor.return_value.__aenter__.return_value = m_cursor

        m_queue = mock.AsyncMock(spec=asyncio.Queue)
        m_queue.empty.return_value = False
        m_queue.get.return_value = aiomqtt.Message(
            topic=m_topic, payload=b"test_payload", qos=1, retain=False, mid=1, properties=None
        )

        publish_task = asyncio.create_task(publish_to_pg_notify(m_queue, m_topic))

        await asyncio.sleep(0)

        publish_task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await publish_task

        m_aenter_m_get_connection.assert_called_once()
        m_connection.cursor.assert_called_once()
        m_cursor.execute.assert_called()
        m_queue.get.assert_called()


async def test_help_send_notification():
    """Test help_send_notification."""
    m_connection = mock.AsyncMock(spec=psycopg.AsyncConnection)
    m_channel = "test/test_help_send_notification"

    with mock.patch("psycopg_async_notify.publish.get_connection", return_value=m_connection) as m_get_connection:
        m_aenter_m_get_connection = m_get_connection.return_value.__aenter__
        m_aenter_m_get_connection.return_value = m_connection

        await help_send_notification(m_channel)

        m_aenter_m_get_connection.assert_called_once()
        m_connection.execute.assert_called()


async def test_help_send_notifcations_continuously():
    """Test help_send_notifcations_continuously."""
    m_connection = mock.AsyncMock(spec=psycopg.AsyncConnection)
    m_channel = "test/test_help_send_notifcations_continuously"

    with mock.patch("psycopg_async_notify.publish.get_connection", return_value=m_connection) as m_get_connection:
        m_aenter_m_get_connection = m_get_connection.return_value.__aenter__
        m_aenter_m_get_connection.return_value = m_connection

        send_notify_task = asyncio.create_task(help_send_notifcations_continuously(m_channel))

        await asyncio.sleep(0)

        send_notify_task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await send_notify_task

        m_aenter_m_get_connection.assert_called_once()
        m_connection.execute.assert_called()


async def test_help_send_notifications_continously_keyboard_interrupt():
    """Test help_send_notifcations_continuously with KeyboardInterrupt."""
    m_connection = mock.AsyncMock(spec=psycopg.AsyncConnection)
    m_channel = "test/test_help_send_notifcations_continuously"

    with mock.patch("psycopg_async_notify.publish.get_connection", return_value=m_connection) as m_get_connection:
        m_aenter_m_get_connection = m_get_connection.return_value.__aenter__
        m_aenter_m_get_connection.return_value = m_connection
        m_connection.execute.side_effect = KeyboardInterrupt

        with pytest.raises(KeyboardInterrupt):
            await help_send_notifcations_continuously(m_channel)

        m_aenter_m_get_connection.assert_called_once()
        m_connection.execute.assert_called()

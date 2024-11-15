"""Test for async listen for notifications."""

import asyncio
from unittest import mock

import psycopg
import psycopg.sql
import pytest

from psycopg_async_notify.execute import config_run, listen_for_notifications


# assert get_connection was called
@pytest.mark.asyncio
async def test_listen_for_notifications_handlers():
    """Test listen_for_notifications.

    Test Plan:
    - Mock get_connection and add_notify_handler and remove_notify_handler
    - Create a queue to hold the notifications
    - Create a task to listen for notifications
    - Sleep for a short time and then cancel the listening task
    - Assert get_connection was called
    """
    with (
        mock.patch("psycopg_async_notify.execute.get_connection") as m_get_connection,
        mock.patch("psycopg_async_notify.db.psycopg.AsyncConnection.add_notify_handler") as m_add_notify_handler,
        mock.patch("psycopg_async_notify.db.psycopg.AsyncConnection.remove_notify_handler") as m_remove_notify_handler,
    ):
        m_queue = asyncio.Queue()
        m_channel = "test_channel"

        m_get_connection.return_value.__aenter__.return_value = mock.AsyncMock(spec=psycopg.AsyncConnection)

        m_handlers = []
        m_add_notify_handler.side_effect = lambda x: m_handlers.append(x)
        m_remove_notify_handler.return_value = mock.AsyncMock()

        # since listen_for_notifications is a coroutine with a infinite loop
        # we ned to run it in a task and cancel after a short time
        listening_task = asyncio.create_task(listen_for_notifications(m_channel, m_queue))

        # wait for the listening task to start listening
        await asyncio.sleep(0.1)

        for handler in m_handlers:
            handler(psycopg.Notify(m_channel, "test_payload", 0))

        # cancel the listening task
        listening_task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await listening_task

        # assert get_connection was called
        assert m_get_connection.call_count == 1

        m_context_manager = m_get_connection.return_value.__aenter__

        # assert the connection was used correctly
        assert m_context_manager.call_count == 1
        assert m_context_manager.return_value.add_notify_handler.call_count == 1
        assert m_context_manager.return_value.execute.call_count >= 1
        assert m_context_manager.return_value.remove_notify_handler.call_count == 1


@pytest.mark.parametrize("error_expected", [psycopg.errors.OperationalError, KeyboardInterrupt])
def test_config_and_run(error_expected):
    """Test config_run.

    Test Plan:
    - Mock listen_for_notifications
    - Call config_run
    - Assert listen_for_notifications was called
    """
    m_channel = "test/test_config_and_run"
    m_queue = asyncio.Queue()
    with (
        mock.patch(
            "psycopg_async_notify.execute.listen_for_notifications", new_callable=mock.AsyncMock
        ) as m_listen_for_notifications,
        mock.patch("psycopg_async_notify.execute.argparse.ArgumentParser.parse_args") as m_parse_args,
    ):
        m_parse_args.return_value = mock.Mock(channel="test/test_config_and_run")
        if error_expected:
            m_listen_for_notifications.side_effect = error_expected
        config_run(m_queue)

        m_listen_for_notifications.assert_called_once_with(m_channel, m_queue)

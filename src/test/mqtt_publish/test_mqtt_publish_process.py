"""Tests for the process module of mqtt_publish."""

from unittest import mock

import pytest

from mqtt_publish.process import publish_to_postgres


@pytest.mark.asyncio
async def test_publish_to_postgres():
    """Test publish_to_postgres."""
    m_topic = "test_topic"
    m_broker = "localhost"

    with (
        mock.patch("mqtt_publish.process.setup_client", new_callable=mock.AsyncMock) as m_setup_client,
        mock.patch(
            "mqtt_publish.process.process_messages_to_queue", new_callable=mock.AsyncMock
        ) as m_process_messages_to_queue,
        mock.patch("mqtt_publish.process.publish_to_pg_notify", new_callable=mock.AsyncMock) as m_publish_to_pg_notify,
    ):
        await publish_to_postgres(m_broker, m_topic)

        m_setup_client.assert_called_once_with(m_broker, m_topic, mock.ANY)
        m_process_messages_to_queue.assert_called_once()
        m_publish_to_pg_notify.assert_called_once()

        m_setup_client.asssert_awaited_once()
        m_process_messages_to_queue.asssert_awaited_once()
        m_publish_to_pg_notify.asssert_awaited_once()

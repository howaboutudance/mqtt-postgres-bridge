"""Mqtt_listen execute tests."""

import logging

from unittest import mock

import pytest

from mqtt_listen.execute import main

_log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_main():
    """Test the main function."""
    m_broker = "test_broker"
    m_topic = "test/test_main"

    with (
        mock.patch("mqtt_listen.execute.setup_client") as m_setup_client,
        mock.patch("mqtt_listen.execute.process_messages_to_log") as m_process_messages,
    ):
        await main(m_broker, m_topic)
        m_setup_client.assert_called_once()
        m_process_messages.assert_called_once()

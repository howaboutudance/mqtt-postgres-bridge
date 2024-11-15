"""Tests for mqtt_publish.config."""

from mqtt_publish.config import CONFIG


def test_config():
    """Test dynaconf CONFIG."""
    assert CONFIG.mqtt_broker

    assert CONFIG.mqtt_broker.host == "localhost"
    assert CONFIG.mqtt_broker.port == 1883

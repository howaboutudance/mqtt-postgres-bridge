"""Test for mqtt_listen config."""

from mqtt_listen.config import CONFIG


def test_config():
    # make sure the config is not empty
    assert CONFIG is not None

    # assert the dynaconf config has the expected keys
    assert "mqtt_broker" in CONFIG
    assert "log_level" in CONFIG
    assert "database" in CONFIG

    # assert the mqtt_broker has the expected keys
    assert "host" in CONFIG.mqtt_broker
    assert "port" in CONFIG.mqtt_broker

    # assert the mqtt_broker has the expected values
    assert CONFIG.mqtt_broker.host == "localhost"
    assert CONFIG.mqtt_broker.port == 1883

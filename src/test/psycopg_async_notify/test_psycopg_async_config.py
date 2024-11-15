"""Tests for psycopg_async_notify.config."""

from psycopg_async_notify.config import CONFIG


def test_config():
    """Test dynaconf CONFIG."""
    assert CONFIG.database

    assert CONFIG.database.host == "127.0.0.1"
    assert CONFIG.database.port == 5432
    assert isinstance(CONFIG.database.user, str)
    assert isinstance(CONFIG.database.password, str)
    assert isinstance(CONFIG.database.name, str)

"""Tests for the psycopg_async_notify.db module."""

from unittest import mock

import psycopg
import pytest

from psycopg_async_notify.config import CONFIG
from psycopg_async_notify.db import get_connection, get_cursor


@pytest.mark.asyncio
async def test_get_connection():
    """Test get_connection."""
    with mock.patch("psycopg_async_notify.db.psycopg.AsyncConnection.connect") as m_connect:
        m_connection = mock.AsyncMock()
        m_connect.return_value = m_connection

        async with get_connection() as conn:
            assert conn is m_connection

        m_connect.assert_called_once_with(
            dbname=CONFIG.database.name,
            user=CONFIG.database.user,
            password=CONFIG.database.password,
            host=CONFIG.database.host,
            port=CONFIG.database.port,
            autocommit=True,
        )


@pytest.mark.asyncio
async def test_get_cursor():
    """Test get_cursor."""
    with mock.patch("psycopg_async_notify.db.get_connection") as m_get_connection:
        # mock a connection and adde to the return value of the async
        # context manager magic method (__aenter__) of m_get_connection
        m_connection = mock.AsyncMock(spec=psycopg.AsyncConnection)

        # doing a intermediate assignment for clarity
        # this first line define m_connection equivalent to
        # get_connection().__aenter__()
        m_aenter_get_connection = m_get_connection.return_value.__aenter__
        m_aenter_get_connection.return_value = m_connection

        # mock a async cursor and add it to the return value of the async
        # context manager magic method (__aenter__) of m_connection.cursor
        m_cursor = mock.AsyncMock(spec=psycopg.AsyncCursor)
        m_cursor.return_value.__aenter__.return_value = m_cursor

        # define the return value of the async context manager magic method
        # (__aenter__) of m_connection.cursor. equivalent relative to
        # get_connection as:
        # get_connection().__aenter__().cursor().__aenter__()
        m_connection.cursor.return_value.__aenter__.return_value = m_cursor

        async with get_cursor() as cursor:
            assert cursor is m_cursor

        m_get_connection.assert_called_once_with(autocommit=True)
        m_connection.cursor.assert_called_once()

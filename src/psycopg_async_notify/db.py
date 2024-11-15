"""Module of database connections and operations."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import psycopg

from psycopg_async_notify.config import CONFIG

_log = logging.getLogger(__name__)


# use an async context manager to yield a connection to the database so it will
# automatically close when the context manager exits
@asynccontextmanager
async def get_connection(autocommit: bool = True) -> AsyncGenerator[psycopg.AsyncConnection, None]:
    """Get a connection context manager to the database.

    :param autocommit: whether to autocommit transactions
    :return: a connection to the database
    """
    conn = await psycopg.AsyncConnection.connect(
        dbname=CONFIG.database.name,
        user=CONFIG.database.user,
        password=CONFIG.database.password,
        host=CONFIG.database.host,
        port=CONFIG.database.port,
        autocommit=autocommit,
    )

    async with conn:
        _log.debug("connected to database")
        yield conn
        _log.debug("closing connection to database")


@asynccontextmanager
async def get_cursor(autocommit: bool = True) -> AsyncGenerator[psycopg.AsyncCursor, None]:
    """Get a cursor context manager to the database.

    :param autocommit: whether to autocommit transactions
    :return: a cursor to the database
    """
    async with get_connection(autocommit=autocommit) as conn:
        async with conn.cursor() as cursor:
            _log.debug("created cursor")
            yield cursor
            _log.debug("closing cursor")

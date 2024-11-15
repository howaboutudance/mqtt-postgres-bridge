"""Main execution entrypoint for application."""

import logging

from psycopg_async_notify.config import CONFIG
from psycopg_async_notify.execute import config_run

_log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=CONFIG.log_level.upper())
    config_run()

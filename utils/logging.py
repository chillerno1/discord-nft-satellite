import os
import logging
import contextlib

from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_PATH = 'logs/'


class RemoveNoise(logging.Filter):

    def __init__(self):
        super().__init__(name='discord.state')

    def filter(self, record):
        if record.levelname == 'WARNING' and 'referencing an unknown' in record.msg:
            return False
        return True


class RemoveRateLimit(logging.Filter):

    def __init__(self):
        super().__init__(name='discord.http')

    def filter(self, record):
        if record.levelname == 'WARNING' and 'We are being rate limited.' in record.msg:
            return False
        return True


def ensure_logs_path_exists():

    """Create a log file directory if it doesn't already exist."""

    if not os.path.exists(LOGS_PATH):
        os.makedirs(os.path.join(ROOT_DIR, LOGS_PATH))


@contextlib.contextmanager
def setup_logging():

    """Logging handler for monitoring errors and warnings."""

    ensure_logs_path_exists()

    try:
        # __enter__
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)
        logging.getLogger('discord.state').addFilter(RemoveNoise())
        logging.getLogger('discord.http').addFilter(RemoveRateLimit())

        message_format = "[%(asctime)s] [%(levelname)s] %(message)s"
        max_bytes = 32 * 1024 * 1024  # 32mb
        format_handler = RichHandler(rich_tracebacks=True,
                                     show_time=True,
                                     show_level=True)
        file_handler = RotatingFileHandler(filename='logs/session.log',
                                           encoding='utf-8',
                                           mode='w',
                                           maxBytes=max_bytes,
                                           backupCount=5)

        logging.basicConfig(
            level="INFO",
            format=message_format,
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                format_handler,
                file_handler
            ],
        )
        log = logging.getLogger()

        yield

    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)
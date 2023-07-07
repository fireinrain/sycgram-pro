from loguru import logger
import sys


def init_logger():
    # log config
    logger.add(
        sys.stderr,
        format="{time} {level} {message}",
        filter="my_module",
        level="INFO",
        enqueue=True
    )
    logger.add(
        './data/log/debug.app.log',
        filter=lambda record: record["level"].name == "DEBUG",
        level="DEBUG",
        enqueue=True,
        retention="21 days"
    )
    logger.add(
        './data/log/info.app.log',
        filter=lambda record: record["level"].name != "DEBUG",
        level="INFO",
        enqueue=True
    )

from dataclasses import dataclass
from os import getenv

from structlog import get_logger

logger = get_logger(__name__)


def get_env(name: str) -> str:
    """Get the value for the env variable with `name`.
    If no value is found, log a message and exits the program with a
    non-zero status code.
    """
    value = getenv(name)
    if not value:
        logger.error("Missing required environment variable", name=name)
        exit(1)
    return value


PRODUCT_IDS = [1, 2, 3, 4, 5]


def product_key(product_id: int) -> str:
    """Create a product key given the `product_id`."""
    return f"product:{product_id}"

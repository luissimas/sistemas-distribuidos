from time import sleep

from common import get_env
from requests import get
from structlog import get_logger

logger = get_logger(__name__)


def main():
    CONSUME_RATE = int(get_env("CONSUME_RATE"))
    DISTRIBUTOR_URL = get_env("DISTRIBUTOR_URL")

    endpoint = f"{DISTRIBUTOR_URL}/product"

    logger.info(
        "Starting consumer app",
        consume_rate=CONSUME_RATE,
        distributor_url=DISTRIBUTOR_URL,
    )

    while True:
        logger.debug("Getting product from distributor API", endpoint=endpoint)
        response = get(endpoint)
        logger.debug(
            "Got response from distributor API", endpoint=endpoint, response=response
        )

        match response.status_code:
            case 200:
                logger.info("Got product from distributor API")
            case 404:
                logger.warn("No product found in distributor API")
            case _:
                logger.error(
                    "Unexpected response from distributor API",
                    status_code=response.status_code,
                    body=response.content,
                )

        sleep(60 / CONSUME_RATE)


if __name__ == "__main__":
    main()

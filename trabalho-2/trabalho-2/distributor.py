from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
from common import PRODUCT_IDS, STOCK_THRESHOLD, get_env, product_key
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from prometheus_client import Gauge, Summary, make_asgi_app
from redis.asyncio import Redis
from structlog import get_logger

logger = get_logger(__name__)

db = Redis(host="redis", port=6379, decode_responses=True)

product_stock = Gauge(
    "distributor_product_count",
    "The total number of products available in stock for prompt delivery",
    labelnames=["product"],
)
product_request_duration = Summary(
    "distributor_product_request_duration", "Duration of requests for products"
)


async def request_production(product_id: int):
    """Request production of more products of `product_id`."""
    logger.info("Requesting production", product_id=product_id)
    # TODO: check if no more requests are pending
    # TODO: put message in MQTT queue
    # TODO: consume from the queue somehow
    ...


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Initializing application")
    for product_id in PRODUCT_IDS:
        logger.info("Initializing metrics for product", product_id=product_id)
        key = product_key(product_id)
        count = await db.get(key)
        if count is None:
            count = 100
            await db.set(key, count)
        else:
            count = int(count)
        product_stock.labels(product=product_id).set(count)
    logger.info("Initialization completed")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/product/{product_id}")
async def get_product(product_id: int, background_tasks: BackgroundTasks):
    with product_request_duration.time():
        key = product_key(product_id)
        stock = int(await db.get(key))

        if stock <= STOCK_THRESHOLD:
            background_tasks.add_task(request_production, product_id=product_id)

        if stock == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)

        await db.decr(key, 1)
        product_stock.labels(product=product_id).set(stock - 1)

        return Response(status_code=HTTPStatus.OK)


app.mount("/metrics", make_asgi_app())


if __name__ == "__main__":
    port = int(get_env("PORT"))
    host = "0.0.0.0"
    logger.info("Starting HTTP server", host=host, port=port)
    uvicorn.run(app, host=host, port=port)

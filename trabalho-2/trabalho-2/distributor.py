from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
from common import PRODUCT_IDS, get_env, pending_request_key, product_key
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from paho.mqtt.client import Client
from prometheus_client import Gauge, Summary, make_asgi_app
from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis
from structlog import get_logger

logger = get_logger(__name__)


STOCK_THRESHOLD = int(get_env("STOCK_THRESHOLD"))

db = AsyncRedis(host="redis", port=6379, decode_responses=True)
sync_db = SyncRedis(host="redis", port=6379, decode_responses=True)
broker = Client()


def on_connect(client, _userdata, _flags, _rc):
    logger.info("Connected to MQTT broker")
    client.subscribe("fabrica1/produzido")
    client.subscribe("fabrica2/produzido")


def on_message(_client, _userdata, msg):
    content = msg.payload.decode()
    product_id, amount = content.split(":")
    logger.info(
        "Received products from factory",
        factory=msg.topic.split("/")[0],
        product_id=product_id,
        amount=amount,
    )
    sync_db.incr(product_key(product_id), amount)
    logger.info("Products added to stock")


broker.on_connect = on_connect
broker.on_message = on_message

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
    pending_request = await db.set(pending_request_key(product_id), 1, get=True)
    if pending_request:
        logger.info(
            "A request for the product is already in progress", product_id=product_id
        )
        return
    request = f"{product_id}:5"
    broker.publish("distribuidor/pedido", request)


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
    http_port = int(get_env("PORT"))
    http_host = "0.0.0.0"
    mqtt_host = "mosquitto"
    mqtt_port = 1883
    logger.info("Connecting to MQTT broker", host=mqtt_host, port=mqtt_port)
    broker.connect(mqtt_host, mqtt_port, 60)
    broker.loop_start()
    logger.info("Starting HTTP server", host=http_host, port=http_port)
    uvicorn.run(app, host=http_host, port=http_port)

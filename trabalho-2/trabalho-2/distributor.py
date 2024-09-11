import uvicorn
from common import PRODUCT_IDS, get_env
from fastapi import FastAPI
from prometheus_client import Gauge, Summary, make_asgi_app
from structlog import get_logger

logger = get_logger(__name__)
app = FastAPI()

product_stock = Gauge(
    "distributor_product_count",
    "The total number of products available in stock for prompt delivery",
    labelnames=["product"],
)
product_request_duration = Summary(
    "distributor_product_request_duration", "Duration of requests for products"
)


@app.get("/product/{id}")
def get_product(id: int):
    # TODO: get product stock from redis and decrement it
    with product_request_duration.time():
        product_stock.labels(product=id).dec()
        return "Hello, world!"


app.mount("/metrics", make_asgi_app())

if __name__ == "__main__":
    # TODO: initialize metrics with redis data
    for id in PRODUCT_IDS:
        product_stock.labels(product=id).set(1000)
    port = int(get_env("PORT"))
    host = "0.0.0.0"
    logger.info("Starting HTTP server", host=host, port=port)
    uvicorn.run(app, host=host, port=port)

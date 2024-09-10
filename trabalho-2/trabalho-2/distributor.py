import uvicorn
from common import get_env
from fastapi import FastAPI
from prometheus_client import make_asgi_app
from structlog import get_logger

logger = get_logger(__name__)
app = FastAPI()


@app.get("/product")
def get_product():
    return "Hello, world!"


app.mount("/metrics", make_asgi_app())

if __name__ == "__main__":
    port = int(get_env("PORT"))
    host = "0.0.0.0"
    logger.info("Starting HTTP server", host=host, port=port)
    uvicorn.run(app, host=host, port=port)

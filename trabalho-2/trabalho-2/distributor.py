import time
import paho.mqtt.client as mqtt
from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
from common import PRODUCT_IDS, STOCK_THRESHOLD, get_env, product_key
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from prometheus_client import Gauge, Summary, make_asgi_app
from redis.asyncio import Redis
from structlog import get_logger

logger = get_logger(__name__)

# Configuração do Redis
db = Redis(host="redis", port=6379, decode_responses=True)

# Métricas
product_stock = Gauge(
    "distributor_product_count",
    "The total number of products available in stock for prompt delivery",
    labelnames=["product"],
)
product_request_duration = Summary(
    "distributor_product_request_duration", "Duration of requests for products"
)

# Configuração do MQTT
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    logger.info("Distribuidor conectado ao broker")
    client.subscribe("fabrica1/produzido")
    client.subscribe("fabrica2/produzido")

def on_message(client, userdata, msg):
    if msg.topic == "fabrica1/produzido":
        mensagem = msg.payload.decode()
        produto, quantidade = mensagem.split(':')
        estoque_atual = await db.get(product_key(produto))
        novo_estoque = (int(estoque_atual) if estoque_atual else 0) + int(quantidade)
        await db.set(product_key(produto), novo_estoque)
        logger.info(f"Distribuidor recebeu da Fábrica 1: {quantidade} unidades de {produto}")
        print_estoque()
    elif msg.topic == "fabrica2/produzido":
        mensagem = msg.payload.decode()
        produto, quantidade = mensagem.split(':')
        estoque_atual = await db.get(product_key(produto))
        novo_estoque = (int(estoque_atual) if estoque_atual else 0) + int(quantidade)
        await db.set(product_key(produto), novo_estoque)
        logger.info(f"Distribuidor recebeu da Fábrica 2: {quantidade} unidades de {produto}")
        print_estoque()

def solicitar_pedido():
    produto_id = random.randint(1, 5)
    quantidade = random.randint(20, 100)
    pedido = f"{produto_id}:{quantidade}"
    logger.info(f"Distribuidor solicitando {quantidade} unidades do produto {produto_id} da Fábrica 2")
    client.publish("distribuidor/pedido", pedido)
    time.sleep(5)  # Delay para simular processo de pedido

async def print_estoque():
    logger.info("Estoque de Produtos:")
    for product_id in PRODUCT_IDS:
        key = product_key(product_id)
        quantidade = await db.get(key)
        logger.info(f"{product_id}: {quantidade if quantidade else 0} unidades")

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
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_start()
    uvicorn.run(app, host=host, port=port)


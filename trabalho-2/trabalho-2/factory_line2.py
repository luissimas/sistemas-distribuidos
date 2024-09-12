import time
from random import randrange

import paho.mqtt.client as mqtt
from structlog import get_logger

logger = get_logger(__name__)

PARTES_POR_PRODUTO = [53, 20, 33, 43, 71]
LINHAS = 7


def on_connect(client, userdata, flags, rc):
    logger.info("Connected to broker")
    client.subscribe("distribuidor/pedido")


def on_message(client, userdata, msg):
    pedido = msg.payload.decode()
    produto_id, quantidade = map(int, pedido.split(":"))
    partes_necessarias = quantidade * PARTES_POR_PRODUTO[produto_id - 1]
    total_pecas = LINHAS * partes_necessarias
    logger.info("Producing products", amount=quantidade, product_id=produto_id)
    time.sleep(randrange(2, 10))  # Simula tempo de produção
    client.publish("fabrica2/produzido", f"{produto_id}:{quantidade}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mosquitto", 1883, 60)

client.loop_forever()

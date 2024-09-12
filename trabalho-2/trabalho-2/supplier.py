from random import randrange
from time import sleep

import paho.mqtt.client as mqtt
from structlog import get_logger

logger = get_logger(__name__)


# Simular peças infinitas
def on_connect(client, userdata, flags, rc):
    logger.info("Connected to broker")
    client.subscribe("fabrica1/pedido")
    client.subscribe("fabrica2/pedido")


def on_message(client, userdata, msg):
    mensagem = msg.payload.decode()
    fabrica, partes_solicitadas = mensagem.split(":")
    partes_solicitadas = int(partes_solicitadas)
    logger.info(
        "Received request for parts", amount=partes_solicitadas, factory=fabrica
    )
    sleep(randrange(5, 15))
    client.publish(f"{fabrica}/entrega", f"Peças entregues: {partes_solicitadas}")
    logger.info("Delivered parts", amount=partes_solicitadas, factory=fabrica)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mosquitto", 1883, 60)

client.loop_forever()

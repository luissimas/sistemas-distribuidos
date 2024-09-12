import time

import paho.mqtt.client as mqtt
from common import PRODUCT_IDS, get_env
from structlog import get_logger

logger = get_logger(__name__)


def on_connect(_client, _userdata, _flags, _rc):
    logger.info("Connected to broker")


def produzir(total_produtos):
    amount = total_produtos / len(PRODUCT_IDS)
    for product_id in PRODUCT_IDS:
        logger.info("Producing products", amount=amount, product_id=product_id)
        client.publish("fabrica1/produzido", f"{product_id}:{amount}")
        time.sleep(2)


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect

    client.connect("mosquitto", 1883, 60)
    client.loop_start()

    production_rate = int(get_env("PRODUCTION_RATE"))

    while True:
        produzir(production_rate)
        time.sleep(60)

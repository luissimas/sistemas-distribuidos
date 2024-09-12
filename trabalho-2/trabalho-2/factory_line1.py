import time

import paho.mqtt.client as mqtt

LINHAS = 5
QUANTIDADE_PRODUTOS = 48


def on_connect(client, userdata, flags, rc):
    print("Fábrica 1 conectada ao broker")


def produzir():
    produtos = ["produto1", "produto2", "produto3", "produto4", "produto5"]
    for produto in produtos:
        total_produtos = LINHAS * QUANTIDADE_PRODUTOS
        print(f"Fábrica 1 produzindo {total_produtos} unidades do {produto}")
        client.publish("fabrica1/produzido", f"{produto}:{total_produtos}")
        time.sleep(2)  # Simula tempo de produção


client = mqtt.Client()
client.on_connect = on_connect

client.connect("mosquitto", 1883, 60)

client.loop_start()

while True:
    produzir()
    time.sleep(10)  # Delay entre ciclos de produção

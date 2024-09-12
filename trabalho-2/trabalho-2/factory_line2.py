import time
import paho.mqtt.client as mqtt
import random

PARTES_POR_PRODUTO = [53, 20, 33, 43, 71]
LINHAS = 7

def on_connect(client, userdata, flags, rc):
    print("Fábrica 2 conectada ao broker")
    client.subscribe("distribuidor/pedido")

def on_message(client, userdata, msg):
    pedido = msg.payload.decode()
    produto_id, quantidade = map(int, pedido.split(':'))
    partes_necessarias = quantidade * PARTES_POR_PRODUTO[produto_id - 1]
    total_pecas = LINHAS * partes_necessarias
    produto = f"produto{produto_id}"
    print(f"Fábrica 2 produzindo {quantidade} unidades do {produto}")
    client.publish("fabrica2/produzido", f"{produto}:{total_pecas}")
    time.sleep(2)  # Simula tempo de produção

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_start()

while True:
    time.sleep(1)  # Mantém o loop ativo


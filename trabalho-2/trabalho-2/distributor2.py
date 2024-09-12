import time
import paho.mqtt.client as mqtt
import queue
import random

# Filas para armazenar os produtos recebidos das fábricas
fila_fabrica1 = queue.Queue()
fila_fabrica2 = queue.Queue()

# Dicionário para armazenar a quantidade de produtos recebidos
estoque_produtos = {
    "produto1": 0,
    "produto2": 0,
    "produto3": 0,
    "produto4": 0,
    "produto5": 0
}

def on_connect(client, userdata, flags, rc):
    print("Distribuidor conectado ao broker")
    client.subscribe("fabrica1/produzido")
    client.subscribe("fabrica2/produzido")

def on_message(client, userdata, msg):
    if msg.topic == "fabrica1/produzido":
        mensagem = msg.payload.decode()
        produto, quantidade = mensagem.split(':')
        estoque_produtos[produto] += int(quantidade)
        print(f"Distribuidor recebeu da Fábrica 1: {quantidade} unidades de {produto}")
        print_estoque()
    elif msg.topic == "fabrica2/produzido":
        mensagem = msg.payload.decode()
        produto, quantidade = mensagem.split(':')
        estoque_produtos[produto] += int(quantidade)
        print(f"Distribuidor recebeu da Fábrica 2: {quantidade} unidades de {produto}")
        print_estoque()

def solicitar_pedido():
    produto_id = random.randint(1, 5)
    quantidade = random.randint(20, 100)
    pedido = f"{produto_id}:{quantidade}"
    print(f"Distribuidor solicitando {quantidade} unidades do produto {produto_id} da Fábrica 2")
    client.publish("distribuidor/pedido", pedido)
    time.sleep(5)  # Delay para simular processo de pedido

def print_estoque():
    print("Estoque de Produtos:")
    for produto, quantidade in estoque_produtos.items():
        print(f"{produto}: {quantidade} unidades")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_start()

while True:
    solicitar_pedido()
    time.sleep(15)  # Solicitações aleatórias com delay


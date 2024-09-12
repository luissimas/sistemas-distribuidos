import time
import paho.mqtt.client as mqtt

# Simular peças infinitas
def on_connect(client, userdata, flags, rc):
    print("Fornecedor conectado ao broker")
    client.subscribe("fabrica1/pedido")
    client.subscribe("fabrica2/pedido")

def on_message(client, userdata, msg):
    mensagem = msg.payload.decode()
    fabrica, partes_solicitadas = mensagem.split(':')
    partes_solicitadas = int(partes_solicitadas)

    print(f"Fornecedor: Recebido pedido de {partes_solicitadas} partes para a {fabrica}")

    # Informar que a entrega está sendo feita
    client.publish(f"{fabrica}/entrega", f"Peças entregues: {partes_solicitadas}")
    print(f"Fornecedor: Entregando {partes_solicitadas} peças para a {fabrica}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_start()

while True:
    time.sleep(1)  # Mantém o loop ativo


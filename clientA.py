import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Conectado com código:", rc)
    client.subscribe("dispositivoB/arquivo_desconhecido")

def on_message(client, userdata, msg):
    print(f"Mensagem recebida no A: {msg.payload.decode()}")

client = mqtt.Client(client_id="dispositivoA")
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 1883, 60)
client.loop_start()

# Simulando envio de arquivo
client.publish("dispositivoA/arquivo", "arquivo123.txt")

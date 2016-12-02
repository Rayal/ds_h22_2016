import paho.mqtt.client as mqtt
import protocol.server_protocol as sp
from protocol.common import *

class Server():
    def __init__(self):
        self.topics = []
        self.clients = []
        self.nicknames = []
        self.games = []

        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, GLOBAL)))
        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, SERVER, SELF)))

        self.client = mqtt.Client()
        self.client.on_connect = lambda client, userdata, flags, rc: self.on_connect(client, userdata, flags, rc)
        self.client.on_message = sp.message_in

        self.client.connect(DEFAULT_SERVER_URL, DEFAULT_SERVER_PORT)

    def start(self):
        self.client.loop_forever()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        for topic in self.topics:
            client.subscribe(topic)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
server = Server()
server.start()

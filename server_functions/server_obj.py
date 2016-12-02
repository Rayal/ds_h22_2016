# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

import paho.mqtt.client as mqtt
from protocol.common import *
import protocol.server_protocol as sp


class Server_CLASS():
    def __init__(self):
        self.clients = []
        self.nicknames = []
        self.topics = []
        self.name = SELF
        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, GLOBAL)))
        self.topics.append("/".join(DEFAULT_ROOT_TOPIC, SERVER, SELF))
        self.mq_client = mqtt.Client()
        self.mq_client.on_connect = self.mqtt_connected
        self.mq_client.on_message = self.message_in
        self.mq_client.connect(DEFAULT_SERVER_URL, DEFAULT_SERVER_PORT)

    def start(self):
        self.mq_client.loop_forever()

    def mqtt_connected(client, userdata, flags, rc):
        LOG.info("Connected with result code "+str(rc))
        for topic in gl_topics:
            client.subscribe(topic)

    def message_in(client, userdata, msg):
        sp.message_in(client, userdata, msg)

    def client_exists(n_client):
        return n_client in gl_clients

    def nickname_exists(n_nick):
        return n_nick in gl_nicknames

    def new_client(n_client, n_nick):
        if not (client_exists(n_client) or nickname_exists(n_nick)):
            gl_clients.append(n_client)
            gl_nicknames.append(n_nick)
            return True
        return False

s = Server_CLASS()
print "Heya"
s.start()

# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.CRITICAL,format=FORMAT)
LOG = logging.getLogger()

import paho.mqtt.client as mqtt
import protocol.client.client_protocol as cp
from protocol.common import *

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/".join((DEFAULT_ROOT_TOPIC, GLOBAL, SELF)))
    client.publish("/".join((DEFAULT_ROOT_TOPIC, GLOBAL)), " ".join((SOUND_OFF, SELF)))

nickname = "DATNAME"
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = lambda client, userdata, msg: cp.message_in(None, client, userdata, msg)
client.connect(DEFAULT_SERVER_URL, DEFAULT_SERVER_PORT)

client.loop_forever()
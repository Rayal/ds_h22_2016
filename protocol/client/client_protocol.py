# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

from protocol.common import *
import protocol.client.global_functions as wf
import protocol.client.server_functions as sf

def message_in(client_obj, mqttclient, userdata, msg):
    if not msg.topic.startswith(DEFAULT_ROOT_TOPIC + "/"):
        return
    topic = msg.topic[DEFAULT_ROOT_LEN:].split("/")
    if topic[0] in CATEGORIES:
        LOG.info("Received message from %s topic"%CATEGORIES[topic[0]])
        if topic[0] == GLOBAL:
            wf.message_in(client_obj, mqttclient, topic[1:], msg.payload.split(" "))
        elif topic[0] == SERVER:
            sf.message_in(client_obj, mqttclient, topic[1:], msg.payload.split(" "))



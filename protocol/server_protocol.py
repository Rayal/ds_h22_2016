# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

from common import *
import global_functions as wf
import server_functions as sf

def message_in(server_obj, client, userdata, msg):
    if not msg.topic.startswith(DEFAULT_ROOT_TOPIC + "/"):
        return
    topic = msg.topic[DEFAULT_ROOT_LEN:].split("/")
    if topic[0] in CATEGORIES:
        LOG.info("Received message from %s topic"%CATEGORIES[topic[0]])
        if topic[0] == GLOBAL:
            wf.message_in(server_obj, client, topic[1:], msg.payload.split(" "))
        elif topic[0] == SERVER:
            sf.message_in(server_obj, client, topic[1:], msg.payload.split(" "))


#def sound_off(client):

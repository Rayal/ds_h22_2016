# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

from protocol.common import *
import protocol.server.global_functions as wf
import protocol.server.server_functions as sf
import protocol.server.game_functions as gf

def message_in(server_obj, client, userdata, msg):
    if not msg.topic.startswith(DEFAULT_ROOT_TOPIC + "/"):
        return
    topic = msg.topic[DEFAULT_ROOT_LEN:].split("/")
    if topic[0] in CATEGORIES:
        LOG.info("Received message from %s topic"%CATEGORIES[topic[0]])
        if topic[0] == GLOBAL:
            wf.message_in(server_obj, client, msg.payload.split(" "))
        elif topic[0] == SERVER and topic[1] == SELF:
            sf.message_in(server_obj, client, msg.payload.split(" "))
        elif topic[0] == GAME and topic[1] == SELF and len(topic) > 2:
            gf.message_in(server_obj, client, topic[2:], msg.payload.split(" "))

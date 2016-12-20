# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

from protocol.common import *

def message_in(client_obj, client, topic_list, payload_list):
    if payload_list[0] in GAME_TYPES:
        LOG.info("Received message of type %s"% GAME_TYPES[payload_list[0]])
    else:
        LOG.debug("Received message of unknown type")
        return

    if payload_list[0] == GAME_SETUP and len(payload_list) >= 2:
        game_setup(client_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == SHIP_POS and len(payload_list) >= 2:
        ship_pos(client_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == READY_TO_START and len(payload_list) >= 2:
        ready_to_start(client_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == START_GAME and len(payload_list) >= 2:
        start_game(client_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == SHOOT and len(payload_list) >= 2:
        shoot(client_obj, client, topic_list, payload_list[1:])
    else:
        LOG.debug("Received message was too short.")

def game_setup(client_obj, mqtt_client, topic_list, payload_list):
    client_obj.game_setup_reply(payload_list[-1])

def ship_pos(client_obj, mqtt_client, topic_list, payload_list):
    client_obj.ship_pos_reply(payload_list[-1])

def ready_to_start(client_obj, mqtt_client, topic_list, payload_list):
    pass

def start_game(client_obj, mqtt_client, topic_list, payload_list):
    response = client_obj.start_game(topic_list[0], payload_list)

def shoot(client_obj, mqtt_client, topic_list, payload_list):
    response = client_obj.shoot(topic_list[0], payload_list)

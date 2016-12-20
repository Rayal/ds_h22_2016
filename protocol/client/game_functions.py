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
    elif (payload_list[0] == SPLASH or payload_list[0] == BOOM or payload_list[0] == SHOOT) and len(payload_list) >= 2:
        shoot(client_obj, client, topic_list, payload_list)
    elif payload_list[0] == HIT and len(payload_list) >= 2:
        hit(client_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == SUNK and len(payload_list) >= 2:
        sunk(client_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == LOST and len(payload_list) >= 2:
        lost(client_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == WON and len(payload_list) >= 2:
        won(client_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == GAME_END and len(payload_list) >= 2:
        game_over(client_obj, client, topic_list, payload_list[1:])
    else:
        LOG.debug("Received message was too short.")

def game_setup(client_obj, mqtt_client, topic_list, payload_list):
    client_obj.game_setup_reply(payload_list[-1])

def ship_pos(client_obj, mqtt_client, topic_list, payload_list):
    client_obj.ship_pos_reply(payload_list[-1])

def ready_to_start(client_obj, mqtt_client, topic_list, payload_list):
    client_obj.ready_to_start_reply(payload_list[-1])

def play_turn(client_obj, mqtt_client, topic_list, payload_list):
    client_obj.play_turn_reply(payload_list[-1])

def shoot(client_obj, mqtt_client, topic_list, payload_list):
    response = client_obj.shoot_reply(topic_list[0], payload_list)

def hit(client_obj, mqtt_client, topic_list, payload_list):
    client_obj.hit(payload_list[-1])

def sunk(client_obj, mqtt_client, topic_list, payload_list):
    client_obj.sunk(payload_list[-1])

def lost(client_obj, mqtt_client, topic_list, payload_list):
    client_obj.lost(payload_list[-1])

def won(client_obj, mqtt_client, topic_list, payload_list):
    client_obj.won(payload_list[-1])

def game_over(client_obj, mqtt_client, topic_list, payload_list):
    client_obj.game_over(payload_list[-1])
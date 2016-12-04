# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

from protocol.common import *

def message_in(server_obj, client, topic_list, payload_list):
    if payload_list[0] in GAME_TYPES:
        LOG.info("Received message of type %s"% GAME_TYPES[payload_list[0]])
    else:
        LOG.debug("Received message of unknown type")
        return

    if payload_list[0] == GAME_SETUP and len(payload_list) >= 2:
        game_setup(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == SHIP_POS and len(payload_list) >= 2:
        ship_pos(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == READY_TO_START and len(payload_list) >= 2:
        ready_to_start(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == START_GAME and len(payload_list) >= 2:
        start_game(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == PLAY_TURN and len(payload_list) >= 2:
        play_turn(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == SHOOT and len(payload_list) >= 2:
        shoot(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == SPLASH and len(payload_list) >= 2:
        splash(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == BOOM and len(payload_list) >= 2:
        boom(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == HIT and len(payload_list) >= 2:
        hit(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == SUNK and len(payload_list) >= 2:
        sunk(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == GAME_OVER and len(payload_list) >= 2:
        game_over(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == REPLAY_GAME and len(payload_list) >= 2:
        replay_game(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == GAME_END and len(payload_list) >= 2:
        game_end(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == DISCONNECT and len(payload_list) >= 2:
        disconnect(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == RECONNECT and len(payload_list) >= 2:
        reconnect(server_obj, client, topic_list, payload_list[1:])
    elif payload_list[0] == NEW_HOST and len(payload_list) >= 2:
        new_host(server_obj, client, topic_list, payload_list[1:])
    else:
        LOG.debug("Received message was too short.")

    def game_setup(server_obj, mqtt_client, topic_list, payload_list):
        response = server_obj.game_setup(topic_list[0], payload_list)
        #TODO: respond to client.
    def ship_pos(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def ready_to_start(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def start_game(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def play_turn(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def shoot(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def splash(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def boom(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def hit(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def sunk(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def game_over(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def replay_game(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def game_end(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def disconnect(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def reconnect(server_obj, mqtt_client, topic_list, payload_list):
        pass
    def new_host(server_obj, mqtt_client, topic_list, payload_list):
        pass

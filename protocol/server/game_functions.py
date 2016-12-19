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
    if response == -1:
        LOG.error("Argument list too short.")
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], "ACK")), NAY)
    elif response == -2:
        LOG.error("Game %s not found."%topic_list[0])
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], "ACK")), NAY)
    elif response == -3:
        LOG.error("Client %s not connected to server."%payload_list[0])
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], "ACK")), NAY)
    elif response == -4:
        LOG.error("Client %s is not the creator for the game %s."%(payload_list[0], topic_list[0]))
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], "ACK")), NAY)
    elif response == -5:
        LOG.error("Unable to set config: %s."%" ".join(payload_list[1:]))
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], "ACK")), NAY)
    elif response == 0:
        LOG.debug("Game config set: %s."%" ".join(payload_list[1:]))
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], "ACK")), "%s %s"%(GAME_SETUP, " ".join(payload_list[1:])), True)
    else:
        LOG.error("Unknown server response.")
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], "ACK")), NAY)

def ship_pos(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.ship_pos(topic_list[0], payload_list)
    if response == -1:
        LOG.error("Argument list too short.")
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], payload_list[0])), "%s %s"%(SHIP_POS, YEA))
    elif response == -2:
        LOG.error("Game %s not found."%topic_list[0])
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], payload_list[0])), "%s %s"%(SHIP_POS, YEA))
    elif response == -3:
        LOG.error("Client %s not connected to server."%payload_list[0])
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], payload_list[0])), "%s %s"%(SHIP_POS, YEA))
    elif response == -4:
        LOG.error("Client %s is not in the game %s."%(payload_list[0], topic_list[0]))
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], payload_list[0])), "%s %s"%(SHIP_POS, YEA))
    elif response == -5:
        LOG.error("Game playing. Unable to set new ship layout.")
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], payload_list[0])), "%s %s"%(SHIP_POS, YEA))
    elif response == -6:
        LOG.error("The number of ships in the layout doesn't match the number expected.")
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], payload_list[0])), "%s %s"%(SHIP_POS, YEA))
    elif response == -7:
        LOG.error("A ship in the layout isn't properly defined.")
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], payload_list[0])), "%s %s"%(SHIP_POS, YEA))
    elif response == -8:
        LOG.error("A ship in the layour exceeds the board dimensions.")
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], payload_list[0])), "%s %s"%(SHIP_POS, YEA))
    elif response == 0:
        LOG.debug("Ship layout set: %s."%" ".join(payload_list[1:]))
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], payload_list[0])), "%s %s"%(SHIP_POS, YEA))
    else:
        LOG.error("Unknown server response.")
        mqtt_publish(mqtt_client, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, topic_list[0], payload_list[0])), "%s %s"%(SHIP_POS, YEA))

def ready_to_start(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.ready_to_start(topic_list[0], payload_list)


def start_game(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.start_game(topic_list[0], payload_list)


def play_turn(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.play_turn(topic_list[0], payload_list)


def shoot(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.shoot(topic_list[0], payload_list)


def splash(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.splash(topic_list[0], payload_list)


def boom(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.boom(topic_list[0], payload_list)


def hit(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.hit(topic_list[0], payload_list)


def sunk(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.sunk(topic_list[0], payload_list)


def game_over(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.game_over(topic_list[0], payload_list)


def replay_game(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.replay_game(topic_list[0], payload_list)


def game_end(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.game_end(topic_list[0], payload_list)


def disconnect(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.disconnect(topic_list[0], payload_list)


def reconnect(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.reconnect(topic_list[0], payload_list)


def new_host(server_obj, mqtt_client, topic_list, payload_list):
    response = server_obj.new_host(topic_list[0], payload_list)

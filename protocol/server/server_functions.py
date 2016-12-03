# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

from protocol.common import *
#from server.server_obj import new_client

def message_in(server_obj, client, topic_list, payload_list):
    if payload_list[0] in SERVER_TYPES:
        LOG.info("Received message of type %s"% SERVER_TYPES[payload_list[0]])
    else:
        LOG.debug("Received message of unknown type")
        return

    if payload_list[0] == CONN_REQ and len(payload_list) >= 3:
        conn_req(server_obj, client, payload_list[1:])

    elif payload_list[0] == GAME_LIST_REQ and len(payload_list) >= 2:
        game_list_req(server_obj, client, payload_list[1:])

    elif payload_list[0] == JOIN_GAME and len(payload_list) >= 3:
        join_game(server_obj, client, payload_list[1:])

    elif payload_list[0] == CREATE_GAME and len(payload_list) >= 2:
        create_game(server_obj, client, payload_list[1:])

    else:
        LOG.debug("Received message was too short.")


def conn_req (server_obj, mqtt, args):
    nick = args[1]
    client = args[0]
    if server_obj.new_client(client, nick):
        mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), YEA)
    else:
        mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), NAY)

def game_list_req(server_obj, mqtt, args):
    client = args[0]
    game_list = server_obj.get_game_list()
    mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), " ".join((GAME_LIST, game_list)))

def join_game(server_obj, mqtt, args):
    pass

def create_game(server_obj, mqtt, args):
    client = args[0]
    game_name = args[1]
    response = server_obj.create_game(game_name, client)
    if response == 0:
        # Game of that name already exists
        msg_topic = "/".join((DEFAULT_ROOT_TOPIC, SERVER, client))
        msg_payload = NAY
        LOG.debug("Sending: %s - %s" % (msg_topic, msg_payload))
        mqtt.publish(msg_topic, msg_payload)

    elif response == -1:
        # Server is full of games
        mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), NAY)
    elif response == -2:
        # Client not connected to server
        mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), NAY)
    else:
        # The response is the game id, in int
        mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), YEA)
        mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, str(response))), YEA)

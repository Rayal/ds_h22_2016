# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

from protocol.common import *
#from server.client_obj import new_client

def message_in(client_obj, client, topic_list, payload_list):
    LOG.info("Received message of type %s"% payload_list[0])
    if payload_list[0] == CONN_REQ:
        conn_req(client_obj, client, payload_list[1:])

    elif payload_list[0] == GAME_LIST_REQ:
        game_list_req(client_obj, client, payload_list[1:])

    elif payload_list[0] == JOIN_GAME:
        join_game(client_obj, client, payload_list[1:])

    elif payload_list[0] == CREATE_GAME:
        create_game(client_obj, client, payload_list[1:])



def conn_req (client_obj, mqtt, args):
    nick = args[1]
    client = args[0]
    if client_obj.new_client(client, nick):
        mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), YEA)
    else:
        mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), NAY)

def game_list_req(client_obj, mqtt, args):
    client = args[0]
    game_list = client_obj.get_game_list()
    mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), " ".join((GAME_LIST, game_list)))

def join_game(client_obj, mqtt, args):
    client = args[0]
    game_id = args[1]
    response = client_obj.join_game(game_id, client)
    if response == 0:
        # The player couldn't join the game
        LOG.debug("Game %s full or already started" % game_id)
        mqtt_publish(mqtt, "/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), NAY)
    elif response == -1:
        # Game not found
        LOG.debug("Game %s not found" % game_id)
        mqtt_publish(mqtt, "/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), NAY)
    elif response == -2:
        # Client not connected to server
        LOG.debug("Client %s not connected to server" % client)
        mqtt_publish(mqtt, "/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), NAY)
    else:
        mqtt_publish(mqtt, "/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), str(response))

def create_game(client_obj, mqtt, args):
    client = args[0]
    game_name = args[1]
    response = client_obj.create_game(game_name, client)
    if response == 0:
        # Game of that name already exists
        mqtt_publish(mqtt, "/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), NAY)
    elif response == -1:
        # Server is full of games
        mqtt_publish(mqtt, "/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), NAY)
    elif response == -2:
        # Client not connected to server
        mqtt_publish(mqtt, "/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), NAY)
    else:
        # The response is the game id, in int
        mqtt_publish(mqtt, "/".join((DEFAULT_ROOT_TOPIC, SERVER, client)), str(response))
        mqtt_publish(mqtt, "/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, str(response))), YEA, True)



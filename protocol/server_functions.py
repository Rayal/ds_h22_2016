# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

from protocol.common import *
#from server.server_obj import new_client

def message_in(server_obj, client, topic_list, payload_list):
    LOG.info("Received message of type %s"% payload_list[0])
    if payload_list[0] == CONN_REQ:
        conn_req(server_obj, client, payload_list[1:])

    elif payload_list[0] == GAME_LIST_REQ:
        game_list_req(server_obj, client, payload_list[1:])

    elif payload_list[0] == JOIN_GAME:
        join_game(server_obj, client, payload_list[1:])

    elif payload_list[0] == CREATE_GAME:
        create_game(server_obj, client, payload_list[1:])



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
    pass

# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.CRITICAL,format=FORMAT)
LOG = logging.getLogger()

from protocol.common import *
#from server.client_obj import new_client

def message_in(client_obj, client, topic_list, payload_list):
    LOG.info("Received message of type %s"% SERVER_TYPES[payload_list[0]])
    if payload_list[0] == CONN_REQ:
        conn_req(client_obj, client, payload_list[1:])

    elif payload_list[0] == GAME_LIST:
        game_list_req(client_obj, client, payload_list[1:])

    elif payload_list[0] == JOIN_GAME:
        join_game(client_obj, client, payload_list[1:])

    elif payload_list[0] == CREATE_GAME:
        create_game(client_obj, client, payload_list[1:])

''' Functions to get the response from the server through mqtt
conn_req - For connection establishment
game_list_req - To get the list of available games
join_game - to join an existing game
create_game - to create a new game
'''

def conn_req(client_obj, mqtt, args):
    LOG.debug("Received message: %s"%args[0])
    client_obj.conn_req(args)

def game_list_req(client_obj, mqtt, args):
    LOG.debug("Received message: %s"%args[0])
    client_obj.game_list(args)

def join_game(client_obj, mqtt, args):
    LOG.debug("Received message: %s" % args[0])
    client_obj.game_list(args)

def create_game(client_obj, mqtt, args):
    LOG.debug("Received message: %s" % args[0])
    client_obj.created_game(args[0])

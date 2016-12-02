from protocol.common import *
#from server.server_obj import new_client

def message_in(client, topic_list, payload_list):
    print "Received message of type %s"% payload_list[0]
    if payload_list[0] == CONN_REQ:
        conn_req(client, payload_list[1:])

    elif payload_list[0] == GAME_LIST_REQ:
        game_list_req(client, payload_list[1:])

    elif payload_list[0] == GAME_LIST:
        game_list(client, payload_list[1:])

    elif payload_list[0] == JOIN_GAME:
        join_game(client, payload_list[1:])

    elif payload_list[0] == CREATE_GAME:
        create_game(client, payload_list[1:])



def conn_req (mqtt, client):
    nick = client[1]
    client = client[0]
    if new_client(client, nick):
        mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, SERVER, client), YEA))
    else:
        mqtt.publish("/".join((DEFAULT_ROOT_TOPIC, SERVER, client), NAY))

def game_list_req(mqtt, client):
    pass

def game_list(mqtt, client):
    pass

def join_game(mqtt, client):
    pass

def create_game(mqtt, client):
    pass

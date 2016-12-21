# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

import paho.mqtt.client as mqtt
import protocol.server.server_protocol as sp
from server_data.game_obj import Game
import random as rnd
from sys import argv

from protocol.common import *

class Server():
    #Constructor. Creates Server object, initializes values.
    def __init__(self, ID = ''):
        if ID == '':
            self.self = SELF + 'S'
        else:
            self.self = ID
        self.topics = []
        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, GLOBAL)))
        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, SERVER, self.self)))

        self.clients = []
        self.nicknames = []

        self.games = []
        self.open_games = []
        self.closed_games = []
        self.free_IDs = range(1, 1000)
        if not DEBUG:
            rnd.shuffle(self.free_IDs)

        self.client = mqtt.Client()
        self.client.on_connect = lambda client, userdata, flags, rc: self.on_connect(client, userdata, flags, rc)
        self.client.on_message = lambda client, userdata, msg: sp.message_in(self, client, userdata, msg)

        self.client.connect(DEFAULT_SERVER_URL, DEFAULT_SERVER_PORT)

    # Starts server thread loop. This is necessary for the mqtt.
    def start(self):
        self.client.loop_forever()

    def stop(self):
        LOG.debug('Received Keyboard Interrupt. Closing server.')
        for game in self.games:
            game.stop()
        self.client.disconnect()

    def add_topic(self, topic):
        self.topics.append(topic)
        self.client.subscribe(topic)

    def remove_topic(self, topic):
        self.topics.remove(topic)
        self.client.unsubscribe(topic)

    # Subscribes to all the necessary MQTT topics
    def sub_to_topics(self):
        for topic in self.topics:
            LOG.info("Subscribing to: %s" % topic)
            self.client.subscribe(topic)

    def remove_game(self, game):
        if game in self.games:
            self.games.remove(game)
        if game in self.open_games:
            self.open_games.remove(game)
        if game in self.closed_games:
            self.closed_games.remove(game)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        LOG.info("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
        self.sub_to_topics()

    # Returns the index the given client, if they are connected to the server.
    # If the client is not connected, this method returns -1
    def client_exists(self, n_client):
        if n_client in self.clients:
            return self.clients.index(n_client)
        return -1

    # Returns the index the given nickname, if they are connected to the server.
    # If the nickname is not connected, this method returns -1
    def nickname_exists(self, n_nick):
        if n_nick in self.nicknames:
            return self.nicknames.index(n_nick)
        return -1

    def client_from_nickname(self, nickname):
        if not nickname in self.nicknames:
            return ''

        return self.clients[self.nicknames.index(nickname)]

    def nickname_from_client(self, client):
        if not client in self.clients:
            return ''

        return self.nicknames[self.clients.index(client)]

    # Return
    def new_client(self, n_client, n_nick):
        if not (self.client_exists(n_client) != self.nickname_exists(n_nick)):
            self.clients.append(n_client)
            self.nicknames.append(n_nick)
            return True
        return False

    def disconnect(self, client):
        if not client in self.clients:
            return
        self.nicknames.remove(self.nicknames[self.clients.index(client)])
        self.clients.remove(client)

    def get_game_list(self):
        LOG.debug(self.games)
        game_list = [game.to_str() for game in self.games]
        LOG.debug(game_list)
        return OBJ_SEP.join(game_list)

    def create_game(self, name, client):
        if not len(self.free_IDs):
            return -1
        if not client in self.clients:
            return -2

        player = self.nicknames[self.clients.index(client)]
        new_game = Game(self, name, player, self.free_IDs.pop(0), client)
        self.games.append(new_game)
        self.open_games.append(new_game)

        self.add_topic("/".join((DEFAULT_ROOT_TOPIC, GAME, self.self, str(new_game.id))))

        return new_game.id

    def join_game(self, g_id, client):
        game = self.game_from_id(g_id, self.open_games) #TODO: Test later
        if not game:
            return -1
        if not client in self.clients:
            return -2

        player = self.nicknames[self.clients.index(client)]

        res = game.add_player(player)
        if res != 0:
            self.open_games.remove(game)
            self.closed_games.append(game)

        if res >= 0:
            LOG.debug("Player %s joined game %s:%d"%(player, game.name, game.id))
            return game.id

        return 0

    def game_from_id(self, game_id, games_list):
        game_ids = [str(game.id) for game in games_list]
        if not game_id in game_ids:
            return None
        return games_list[game_ids.index(game_id)]

    def game_setup(self, game_id, args_list):
        if len(args_list) < 4:
            return -1

        game = self.game_from_id(game_id, self.games)
        if not game:
            return -2

        client_name = args_list[0]
        if not client_name in self.clients:
            return -3

        if game.client != client_name: # Not necessary to do this here. We could also do this in game_obj. But it IS necessary to do it somewhere.
            return -4

        size_x, size_y = args_list[1:3]
        ship_list = args_list[3:]

        if game.configure((size_x, size_y), ship_list):
            return 0
        return -5

    def ship_pos(self, game_id, args_list):
        if len(args_list) < 2:
            return -1

        game = self.game_from_id(game_id, self.games)
        if not game:
            return -2

        client = args_list[0]
        if not client in self.clients:
            return -3

        player = self.nicknames[self.clients.index(client)]

        res = game.set_ships(player, args_list[1])

        if res: # set_ships already gives different return codes. Make sure they don't clash with this method's.
            res -= 3
        return res

    def start_game(self, game_id, args_list):
        game = self.game_from_id(game_id)
        if not game:
            return False
        return game.start_game()

    def shoot(self, game_id, args_list):
        client_name = args_list[0]
        if not client_name in self.clients:
            return
        player = self.nicknames[self.clients.index(client)]

        game = self.game_from_id(game_id)
        if not game:
            return

        game.shoot(player, args_list[2:], args_list[1])

if len(argv) >= 2:
    server = Server(argv[1])
else:
    server = Server()
try:
    server.start()
except KeyboardInterrupt:
    server.stop()

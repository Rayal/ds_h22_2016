# Setup Python logging --------------------------------------------------------
import logging
FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
LOG = logging.getLogger()

import paho.mqtt.client as mqtt
import protocol.server.server_protocol as sp
from protocol.common import *
from server_data.game_obj import Game
import random as rnd

class Server():
    def __init__(self):
        self.topics = []
        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, GLOBAL)))
        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, SERVER, SELF)))

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

    def start(self):
        self.client.loop_forever()

    def sub_to_topics(self):
        for topic in self.topics:
            LOG.info("Subscribing to: %s" % topic)
            self.client.subscribe(topic)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        LOG.info("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.sub_to_topics()

    def client_exists(self, n_client):
        return n_client in self.clients

    def nickname_exists(self, n_nick):
        return n_nick in self.nicknames

    def new_client(self, n_client, n_nick):
        if not (self.client_exists(n_client) != self.nickname_exists(n_nick)):
            self.clients.append(n_client)
            self.nicknames.append(n_nick)
            return True
        return False

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

        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, str(new_game.id))))
        self.sub_to_topics()

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

        client_name = args_list[0]
        if not client_name in self.clients:
            return -3

        player = self.nicknames[self.clients.index(client)]

        res = game.set_ships(player, args_list[1])

        if res: # set_ships already gives different return codes. Make sure they don't clash with this method's.
            res -= 3
        return res

    def ready_to_start(self, game_id, args_list):
        pass

    def start_game(self, game_id, args_list):
        pass

    def play_turn(self, game_id, args_list):
        pass

    def shoot(self, game_id, args_list):
        pass

    def splash(self, game_id, args_list):
        pass

    def boom(self, game_id, args_list):
        pass

    def hit(self, game_id, args_list):
        pass

    def sunk(self, game_id, args_list):
        pass

    def game_over(self, game_id, args_list):
        pass

    def replay_game(self, game_id, args_list):
        pass

    def game_end(self, game_id, args_list):
        pass

    def disconnect(self, game_id, args_list):
        pass

    def reconnect(self, game_id, args_list):
        pass

    def new_host(self, game_id, args_list):
        pass


server = Server()
server.start()

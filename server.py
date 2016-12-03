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
        self.free_IDs = range(1, 1000)
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
        if not (self.client_exists(n_client) or self.nickname_exists(n_nick)):
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
        if name in [game.name for game in self.games]:
            return 0

        if not len(self.free_IDs):
            return -1

        if not client in self.clients:
            return -2

        player = self.nicknames[self.clients.index(client)]
        new_game = Game(self, name, player, self.free_IDs.pop(0), client)
        self.games.append(new_game)

        self.topics.append("/".join((DEFAULT_ROOT_TOPIC, GAME, SELF, str(new_game.id))))
        self.sub_to_topics()

        return new_game.id

server = Server()
server.start()

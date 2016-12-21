from protocol.common import *

import numpy as np
from collections import defaultdict
import threading
import server_data.game_states as states
from time import sleep, time

def get_ship(world, size, initial, horizontal):
    x1, y1 = initial
    if horizontal:
        return world[y1][x1 + size]
    else:
        return world.T[x1][y1 + size]

def set_ship(world, args, horizontal):
    size, x1, y1 = args
    try:
        if horizontal:
            if list(world[y1][x1:x1 + size]) != [0] * size:
                print (args, list(world[y1][x1:x1 + size]))
                return False
            world[y1][x1:x1 + size] = 1
        else:
            if list(world.T[x1][y1:y1 + size]) != [0] * size:
                print (args, list(world[y1][x1:x1 + size]))
                return False
            world.T[x1][y1:y1 + size] = 1
    except IndexError:
        return False
    return True


class Game():
    def __init__(self, parent, name, player, n_id, client):
        self.name = name
        self.players = [player]
        self.parent = parent
        self.id = n_id
        self.client = client
        self.config_done = False
        self.boards = {}
        self.player_ships = {}

        self.state = states.INIT
        self.ready_to_start = False
        self.playing = False
        self.game_running = True
        self.thread = threading.Thread(target = lambda:self.game_thread())

        self.turn_waiting = False
        self.turn_wait_time = 0
        self.turn_waiting_since = 0

        self.thread.start()

    def game_thread(self):
        LOG.debug('Game %d thread started.' % self.id)
        self.last_action_time = int(time())
        while self.game_running:
            if int(time()) - self.last_action_time > states.DEFAULT_WAIT_TIME:
                break
            sleep(1)
            if self.state == states.INIT:
                if self.config_done and self.check_ready():
                    self.state = states.WAITING_TO_START
                    continue
            elif self.state == states.WAITING_TO_START:
                if not (self.config_done and self.check_ready()):
                    self.state = states.INIT
                    continue
                mqtt_publish(
                    self.parent.client,
                    '/'.join(
                        (DEFAULT_ROOT_TOPIC,
                            GAME,
                            self.parent.self,
                            str(self.id),
                            ACK)),
                        START_GAME)
                self.state = states.PLAY
                self.start_game()
            elif self.state == states.PLAY:
                self.playing = True
                if len(self.activeplayers) == 1:
                    self.state = states.POST_PLAY
                    continue
                if self.turn_waiting:
                    if int(time()) - self.turn_waiting_since >= self.turn_wait_time or len(self.moves) == len(self.activeplayers):
                        self.turn_timeout()
                    continue
                self.moves = defaultdict(lambda:False)
                for player in self.activeplayers:
                    self.send_turn(player)
                self.turn_waiting = True
                self.turn_wait_time = states.DEFAULT_TURN_SPEED
                self.turn_waiting_since = int(time())
            elif self.state == states.POST_PLAY:
                self.winner()
                break
            else:
                pass
        # Cleanup before destroying.
        mqtt_publish(self.parent.client,
            '/'.join((
                    DEFAULT_ROOT_TOPIC,
                    GAME,
                    self.parent.self,
                    str(self.id),
                    ACK)),
                'GAME_OVER', True)
        self.parent.remove_topic('/'.join((DEFAULT_ROOT_TOPIC, GAME, self.parent.self, str(self.id))))
        LOG.debug('Game %d thread ended.' % self.id)
        self.parent.remove_game(self)
        del self

    def stop(self):
        self.game_running = False

    def turn_timeout(self):
        self.turn_waiting = False
        self.turn_wait_time = states.DEFAULT_WAIT_TIME
        for player in self.activeplayers:
            if self.moves[player] == False:
                self.player_lost(player)

    def send_turn(self, player):
        mqtt_publish(self.parent.client,
            '/'.join((DEFAULT_ROOT_TOPIC,
                GAME,
                self.parent.self,
                str(self.id),
                self.parent.client_from_nickname(player)
                )),
            PLAY_TURN)

    def check_ready(self):
        if len(self.players) < 2 or len(self.boards) < len(self.players):
            self.ready_to_start = False
            return False
        self.ready_to_start = True
        return True

    def add_player(self, player):
        self.last_action_time = int(time())
        if len(self.players) == 3:
            return -1
        self.players.append(player)
        if len(self.players) == 3:
            return 1
        return 0

    def to_str(self):
        name = "%d%s%s%s" % (self.id, SUB_OBJ_SEP, self.name, SUB_OBJ_SEP)
        name += SUB_OBJ_SEP.join(self.players)
        return name

    def configure(self, size, ship_list):
        self.last_action_time = int(time())
        if self.config_done: # Conf can only be done once.
            return False

        self.conf = ' '.join(list(size) + ship_list)
        ship_list = np.array(ship_list).astype(int)
        size = np.array(size).astype(int)
        if size[0] > 10 or size[1] > 10:
            return False
        if sum(ship_list) > 2 * np.prod(size) / 3:
            return False

        self.size = size
        self.ship_list = defaultdict(int)

        for ship in ship_list:
            self.ship_list[ship] += 1

        self.config_done = True
        return True

    def get_conf(self):
        ret = str(self.size).strip('[]')
        for i in self.ship_list:
            for j in range(ship_list[i]):
                ret += ' ' + str(i)

        return ret

    def set_ships(self, player, ship_list):
        self.last_action_time = int(time())
        if not self.config_done:
            return -6

        if not player in self.players:
            return -1

        if self.playing:
            return -2

        ship_list = ship_list.split(OBJ_SEP)
        if len(ship_list) != sum(self.ship_list.values()):
            return -3

        board = np.zeros(self.size)
        for ship in ship_list:
            ship = ship.split(SUB_OBJ_SEP)
            if len(ship) != 4:
                del board
                return -4

            if not set_ship(board,
                    np.array(ship[:-1]).astype(int),
                    ship[-1] == HORIZONTAL):
                del board
                return -5

        self.player_ships[player] = ship_list
        LOG.debug("Player %s board"%player)

        self.boards[player] = board
        return 0

    def start_game(self):
        self.state = states.PLAY
        self.activeplayers = [] + self.players
        return True

    def shoot(self, player, coords):
        self.last_action_time = int(time())
        try:
            coords = list(np.array(coords).astype(int))
        except ValueError:
            return None
        victim = self.players[self.players.index(player) - 1]
        self.moves[player] = True
        if self.boards[victim][coords[1]][coords[0]] != 0:
            self.shot_message(victim, coords, player)
            self.check_sunk(victim, coords[:2])
            return True
        return False

    def shot_message(self, player, coords, aggressor):
        client = self.parent.client_from_nickname(player)
        mqtt_publish(self.parent.client,
            '/'.join((DEFAULT_ROOT_TOPIC,
                GAME,
                self.parent.self,
                str(self.id),player)),
            ' '.join((HIT, str(coords).strip('[]'), aggressor)))

    def sunk_message(self, ship, player):
        for player in self.players:
            mqtt_publish(self.parent.client,
                '/'.join(
                    (DEFAULT_ROOT_TOPIC,
                    GAME,
                    self.parent.self,
                    str(self.id),
                    player)),
                ' '.join((SUNK, str(ship), player)))

    def player_lost(self, player):
        for p in self.players:
            mqtt_publish(self.parent.client,
                '/'.join((
                    DEFAULT_ROOT_TOPIC,
                    GAME,
                    self.parent.self,
                    str(self.id),
                    p)),
                ' '.join((LOST, player)))
        self.activeplayers.remove(player)

    def winner(self):
        for player in self.players:
            mqtt_publish(self.parent.client,
                '/'.join((
                    DEFAULT_ROOT_TOPIC,
                    GAME,
                    self.parent.self,
                    str(self.id),
                    player)),
                ' '.join((WON, self.activeplayers[0])))

    def check_sunk(self, player, coords):
        n_x, n_y = coords
        d_ship = None
        for ship in self.player_ships[player]:
            size, x, y, d = ship
            if d == HORIZONTAL:
                if n_x >= x and (n_x < x + size) and n_y == y:
                    d_ship = ship
                    break
            else:
                if n_y >= y and (n_y < y + size) and n_x == x:
                    d_ship = ship
                    break


        ship = list(get_ship(self.boards[player], d_ship[0], d_ship[1:-1], d_ship[-1] == HORIZONTAL))

        if ship.count(2) == len(ship):
            self.player_ships[player].remove(d_ship)
            self.sunk_message(len(ship), player)
            if len(self.playerself.player_ships[player]) == 0:
                self.player_lost(player)

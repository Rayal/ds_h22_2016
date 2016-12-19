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
            if list(world[y1][x1 + size]) != [0] * size:
                return False
            world[y1][x1 + size] = 1
        else:
            if list(world.T[x1][y1 + size]) != [0] * size:
                return False
            world.T[x1][y1 + size] = 1
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
        self.game_running = True
        self.thread = threading.Thread(target = lambda:self.game_thread())

        self.waiting = False
        self.wait_time = 0
        self.waiting_since = 0

        self.thread.start()
        self.player_moves = defaultdict(lambda:(None, None))

    def game_thread(self):
        LOG.debug('Game %d thread started.' % self.id)
        while self.game_running:
            sleep(1)
            if self.state == states.INIT:
                if self.config_done and self.check_ready():
                    self.state = states.WAITING_TO_START
                    continue
            elif self.state == states.WAITING_TO_START:
                if not (self.config_done and self.check_ready()):
                    self.state = states.INIT
                    continue
                self.parent.ready_to_start(self, self.get_conf())
            elif self.state == states.PLAY:
                if self.waiting:
                    if int(time.time()) - self.waiting_since >= wait_time:
                        self.turn_timeout()
                    else:
                        continue
                for player in self.activeplayers:
                    self.send_turn(player)
                self.waiting = True
                self.wait_time = states.DEFAULT_TURN_SPEED
                self.waiting_since = int(time.time())
                pass
            elif self.state == states.POST_PLAY:
                pass
            else:
                pass
        LOG.debug('Game %d thread ended.' % self.id)
        return

    def stop(self):
        self.game_running = False

    def turn_timeout(self):
        self.waiting = False
        self.wait_time = states.DEFAULT_WAIT_TIME
        for player in self.activeplayers:
            if self.player_moves[player] == (None, None, None):
                self.activeplayers.remove(player)
            else:
                self.play_move(player, self.player_moves[player])

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
        if len(players) < 2 or len(boards) < len(players):
            self.ready_to_start = False
            return False
        self.ready_to_start = True
        return True

    def add_player(self, player):
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
        if self.config_done: # Conf can only be done once.
            return False

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
        if self.state != states.WAITING_TO_START:
            return False
        self.state = states.PLAY
        self.activeplayers = [] + self.players
        return True

    def shot_message(self, player, coords, aggressor):
        client = self.parent.client_from_nickname(player)
        mqtt_publish(self.parent.client,
        '/'.join((DEFAULT_ROOT_TOPIC, GAME, self.parent.self, str(self.id), client)),
        ' '.join((HIT, ) + coords[0] + (aggressor, )))

    def check_sunk(self, player, coords):
        n_x, n_y = coords
        ship = None
        for [size, x, y, d] in self.player_ships[player]:
            if d == HORIZONTAL:
                if n_x >= x and (n_x < x + size) and n_y == y:
                    ship = [size, x, y, d]
                    break
            else:
                if n_y >= y and (n_y < y + size) and n_x == x:
                    ship = [size, x, y, d]
                    break


        ship = list(get_ship(self.boards[player], ship[0], ship[1:-1], ship[-1] == HORIZONTAL))

        return ship.count(2) == len(ship)

    def play_move(self, player, move):
        if move[0] >= self.size[0] or move[1] >= self.size[1]:
            return False
        if move[2] == player:
            return False

        victim = self.boards[self.players[move[2]]]

        if victim [move[1]][move[0]] != 0:
            victim [move[1]][move[0]] = 2
            self.shot_message(move[2], move[:2], player)
            self.check_sunk(move[2], move[:2])
            return True
        return False

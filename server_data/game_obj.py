from protocol.common import *
import numpy as np
from collections import defaultdict

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
            world[y1][x1 + size] = 1
        else:
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
        self.config = False
        self.boards = {}

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
        if self.config: # Conf can only be done once.
            return False

        ship_list = np.array(ship_list).astype(int)
        size = np.array(size).astype(int)
        if sum(ship_list) > 2 * np.prod(size) / 3:
            return False

        self.size = size
        self.ship_list = defaultdict(int)

        for ship in ship_list:
            self.ship_list[ship] += 1

        self.config = True
        return True

    def set_ships(self, player, ship_list):
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

            if not set_ship(board, np.array(ship[:-1]).astype(int), ship[-1] == HORIZONTAL):
                del board
                return -5

        LOG.debug("Player %s board"%player)
        print(board)

        self.boards[player] = board
        if len(self.boards) == len(self.players):
            #Send "Ready to Play"
            pass
        return 0

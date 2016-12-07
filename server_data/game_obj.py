from protocol.common import *
import numpy as np
from collections import defaultdict

def get_ship(size, initial, orientation, world):
    x1, y1 = initial
    if not orientation:
        return world[y1][x1 + size]
    else:
        return world.T[x1][y1 + size]

def set_ship(size, initial, orientation, world):
    x1, y1 = initial
    if not orientation:
        world[y1][x1 + size] = 1
    else:
        world.T[x1][y1 + size] = 1


class Game():
    def __init__(self, parent, name, player, n_id, client):
        self.name = name
        self.players = [player]
        self.parent = parent
        self.id = n_id
        self.client = client

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
        ship_list = np.array(ship_list).astype(int)
        size = np.array(size).astype(int)
        if sum(ship_list) > 2 * np.prod(size) / 3:
            return False

        board = np.zeros(size)
        self.ship_list = defaultdict(int)

        for ship in ship_list:
            self.ship_list[ship] += 1

        return True

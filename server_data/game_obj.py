from protocol.common import *

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

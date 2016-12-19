import copy, random

def print_board(board, nick):

    print "The " + nick + "'s board look like this: \n"

    # print the horizontal numbers
    print " ",
    for i in range(10):
        print "  " + str(i + 1) + "  ",
    print "\n"

    for i in range(10):

        # print the vertical line number
        if i != 9:
            print str(i + 1) + "  ",
        else:
            print str(i + 1) + " ",

        # print the board values, and cell dividers
        playerID=1

        for j in range(10):
            if board[i][j] == -1:
                print ' ',
            elif playerID == "1":
                print board[i][j],
            elif playerID == "2":
                if board[i][j] == "*" or board[i][j] == "$":
                    print board[i][j],
                else:
                    print " ",

            if j != 9:
                print " | ",
        print

        # print a horizontal line
        if i != 9:
            print "   ----------------------------------------------------------"
        else:
            print


def user_place_ships(board, ships, nick, playerID):
    for ship in ships.keys():

        # get coordinates from user and vlidate the postion
        valid = False
        while (not valid):

            print_board(board, nick)
            print "Placing a " + ship
            x, y = get_coor()
            ori = v_or_h()
            valid = validate(board, ships[ship], x, y, ori)
            if not valid:
                print "Cannot place a ship there.\nPlease take a look at the board and try again."
                raw_input("Hit ENTER to continue")

        # place the ship
        board = place_ship(board, ships[ship], ship[0], ori, x, y)
        print_board(board, nick)

    raw_input("Done placing user ships. Hit ENTER to continue")
    return board


def computer_place_ships(board, ships):
    for ship in ships.keys():

        # genreate random coordinates and vlidate the postion
        valid = False
        while (not valid):

            x = random.randint(1, 10) - 1
            y = random.randint(1, 10) - 1
            o = random.randint(0, 1)
            if o == 0:
                ori = "v"
            else:
                ori = "h"
            valid = validate(board, ships[ship], x, y, ori)

        # place the ship
        print "Computer placing a/an " + ship
        board = place_ship(board, ships[ship], ship[0], ori, x, y)

    return board


def place_ship(board, ship, s, ori, x, y):
    # place ship based on orientation
    if ori == "v":
        for i in range(ship):
            board[x + i][y] = s
    elif ori == "h":
        for i in range(ship):
            board[x][y + i] = s

    return board


def validate(board, ship, x, y, ori):
    # validate the ship can be placed at given coordinates
    if ori == "v" and x + ship > 10:
        return False
    elif ori == "h" and y + ship > 10:
        return False
    else:
        if ori == "v":
            for i in range(ship):
                if board[x + i][y] != -1:
                    return False
        elif ori == "h":
            for i in range(ship):
                if board[x][y + i] != -1:
                    return False

    return True


def v_or_h():
    # get ship orientation from user
    while (True):
        user_input = raw_input("vertical or horizontal (v,h) ? ")
        if user_input == "v" or user_input == "h":
            return user_input
        else:
            print "Invalid input. Please only enter v or h"


def get_coor():
    while (True):
        user_input = raw_input("Please enter coordinates (row,col) ? ")
        try:
            # see that user entered 2 values seprated by comma
            coor = user_input.split(",")
            if len(coor) != 2:
                raise Exception("Invalid entry, too few/many coordinates.");

            # check that 2 values are integers
            coor[0] = int(coor[0]) - 1
            coor[1] = int(coor[1]) - 1

            # check that values of integers are between 1 and 10 for both coordinates
            if coor[0] > 9 or coor[0] < 0 or coor[1] > 9 or coor[1] < 0:
                raise Exception("Invalid entry. Please use values between 1 to 10 only.")

            # if everything is ok, return coordinates
            return coor

        except ValueError:
            print "Invalid entry. Please enter only numeric values for coordinates"
        except Exception as e:
            print e


def make_move(board, x, y):
    # make a move on the board and return the result, hit, miss or try again for repeat hit
    if board[x][y] == -1:
        return "miss"
    elif board[x][y] == '*' or board[x][y] == '$':
        return "try again"
    else:
        return "hit"





def main(clientObj):
    nickname = clientObj.nickname

    # types of ships
    ships = {"Aircraft Carrier": 5,
             "Battleship": 4,
             "Submarine": 3,
             "Destroyer": 3,
             "Patrol Boat": 2}

    # setup blank 10x10 board
    board = []
    for i in range(10):
        board_row = []
        for j in range(10):
            board_row.append(-1)
        board.append(board_row)

    # setup user and computer boards
    user_board = copy.deepcopy(board)
    #comp_board = copy.deepcopy(board)

    # add ships as last element in the array
    user_board.append(copy.deepcopy(ships))
    #comp_board.append(copy.deepcopy(ships))

    # ship placement
    user_board = user_place_ships(user_board, ships)
    #comp_board = computer_place_ships(comp_board, ships)

    # game main loop
    while (1):

        # player 1 move
        print_board('player_board', nickname)
        comp_board = user_move(comp_board)

        # display user board
        print_board("u", user_board)
        raw_input("To end computer turn hit ENTER")
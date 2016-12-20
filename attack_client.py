

def print_board(s, board):



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
        for j in range(10):
            if board[i][j] == -1:
                print ' ',
            elif s == "u":
                print board[i][j],
            elif s == "c":
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


def user_move(board, isHit):
    # get coordinates from the user and try to make move
    # if move is a hit, check ship sunk and win condition
    while (True):
        x, y = get_coor()
        #res = make_move(board, x, y)
        res=isHit
        if res == "hit":
            print "Hit at " + str(x + 1) + "," + str(y + 1)
            #check_sink(board, x, y)
            board[x][y] = '$'
            #if check_win(board):
                #return "WIN"
        elif res == "miss":
            print "Sorry, " + str(x + 1) + "," + str(y + 1) + " is a miss."
            board[x][y] = "*"
        elif res == "try again":
            print "Sorry, that coordinate was already hit. Please try again"

        if res != "try again":
            return board

def computer_move(board):
    pass

def main(coordinate, isHit):
    # types of ships
    oppo_board = [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
             [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
             [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
             [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
             [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
             [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
             [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
             [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
             [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
             [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
             {'Submarine': 3, 'Battleship': 4, 'Patrol Boat': 2, 'Aircraft Carrier': 5, 'Destroyer': 3}
             ]

    # setup blank 10x10 board
    board = []
    for i in range(10):
        board_row = []
        for j in range(10):
            board_row.append(-1)
        board.append(board_row)

    # setup user and computer boards
    #user_board = copy.deepcopy(board)
    #comp_board = copy.deepcopy(board)

    # add ships as last element in the array
    #user_board.append(copy.deepcopy(ships))
    #comp_board.append(copy.deepcopy(ships))

    # ship placement
    #user_board = user_place_ships(user_board, ships)
    #comp_board = computer_place_ships(comp_board, ships)

    # game main loop
    while (1):

        # user move
        #print_board("c", comp_board)
        oppo_board = user_move(oppo_board, isHit)

        # check if user won
        if oppo_board == "WIN":
            print "User WON! :)"
            quit()

        # display current computer board
        print_board("c", oppo_board)

        #raw_input("To end user turn hit ENTER")

        # computer move
        #user_board = computer_move(user_board)

        # check if computer move
        #if user_board == "WIN":
            #print "Opponenet WON! :("
            #quit()

        # display user board
        #print_board("u", user_board)
        #raw_input("To end computer turn hit ENTER")


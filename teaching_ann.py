# Board dimensions
BOARD_WIDTH = 20
BOARD_HEIGHT = 20

class Snake:
    def __init__(self, id, position, moveDecider = "random"):
        self.id = id
        self.head_color, self.body_color = generateColor()
         
        self.lastDirection = lambda :(position[-1][0]-position[-2][0], position[-1][1]-position[-2][1])
        # List where, position[0] == tail, position[-1] == head
        self.position = position
        for pos in position:
            BOARD[pos[1]][pos[0]] = id
        
        # Function which gets called when the snake needs to make a move.
        self.moveDecider = self.randomMove


def game():
    BOARD = [[None for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
    FOOD_LOC = None

# All possible moves for snake, that, dont hit itself.
def possibleMoves(self, startPos):
    moves = []
    # Array of all occupied positions
    occupied = reduce(lambda a,b: a+b, [snake.position for snake in SNAKES])

    for move in (UP, DOWN, LEFT, RIGHT):
        frm = startPos
        new_x = (frm[0] + move[0]) % BOARD_WIDTH
        new_y = (frm[1] + move[1]) % BOARD_HEIGHT

        # Väldib endasse ja teise snek-i sisse sõitmist
        if (new_x, new_y) not in occupied:
            moves.append(move)            

    return moves

# Returns a random move from possibleMoves()
def randomMove(self):
    moves = self.possibleMoves(self.position[-1])
    # If no move is possible, choose random
    if len(moves) == 0:
        moves = [UP, DOWN, LEFT, RIGHT]
    return random.choice(moves)
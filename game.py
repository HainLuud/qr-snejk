import pygame
import random
import sys
from functools import reduce

###################### BOARD/WINDOW ######################
# Colours
TILE_COLOR = (50, 50, 50)
BODY_COLOR = (245, 245, 245)
HEAD_COLOR = (255,187,51)
FOOD_COLOR = (255,64,25)

# Board dimensions
BOARD_WIDTH = 20
BOARD_HEIGHT = 20
BLOCK_SIZE = 20
WINDOW_WIDTH = BOARD_WIDTH*BLOCK_SIZE
WINDOW_HEIGHT = BOARD_HEIGHT*BLOCK_SIZE

BOARD = [[None for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]

FOOD_LOC = None

###################### GAME SETTINGS ######################
# Game will advance by {GAME_SPEED} frames per second
GAME_SPEED = 10

###################### SNAKE ######################
# On the next move snakes head will be moved by (x, y)
UP, DOWN, LEFT, RIGHT = ((0,1), (0,-1), (-1,0), (1,0))


class Snake:
    def __init__(self, id, position, moveDecider = "random"):
        self.id = id
        
        self.ate = False
        self.lastDirection = (position[-1][0]-position[-2][0], position[-1][1]-position[-2][1])
        # List, position[0] == tail, position[-1] == head
        self.position = position
        for pos in position:
            BOARD[pos[1]][pos[0]] = id
        
        if moveDecider == "random":
            self.moveDecider = self.randomMove
        elif moveDecider == "Siia tuleks lisada oma decideri nimi":
            pass
        
    # All possible moves for snake, that dont hit itself.
    def possibleMoves(self):
        moves = []
        for move in (UP, DOWN, LEFT, RIGHT):
            head = self.position[-1]
            new_x = (head[0] + move[0]) % BOARD_WIDTH
            new_y = (head[1] + move[1]) % BOARD_HEIGHT

            # Väldib iseendale otsa sõitmist
            if BOARD[new_y][new_x] != self.id:
                moves.append(move)

        return moves

    # Returns a random move from possibleMoves()
    def randomMove(self):
        moves = self.possibleMoves()
        # If no move is possible, choose random
        if len(moves) == 0:
            moves = [UP, DOWN, LEFT, RIGHT]
        return random.choice(moves)

    # Moves the sanake based on it's moveDecider
    def move(self):
        direction = self.moveDecider()
        head = self.position[-1]

        # Direction coordinates get added to head.
        # % - if coordinate exceeds board size, start from other end
        new_x = (head[0] + direction[0]) % BOARD_WIDTH
        new_y = (head[1] + direction[1]) % BOARD_HEIGHT
        new_head = (new_x, new_y)
        self.position.append(new_head)
        
        # If snake hits food, dont remove tail block
        if BOARD[new_y][new_x] == 0:
            tail = self.position[0]
            generateFood()
        else:
            tail = self.position.pop(0)
    	
        # BOARD changes 
        # Adds new head to board
        BOARD[new_head[1]][new_head[0]] = self.id
        # Removes tail from board
        # TODO: Kui teine uss liigutab sama käigu ajal pea sellele kohale, siis läheb katki
        BOARD[tail[1]][tail[0]] = None

# All the snakes will be stored in array
SNAKES = []
SNAKES.append(Snake(1, [(1,1), (2,1), (3,1), (4,1), (5,1)]))
SNAKES.append(Snake(2, [(5,5), (6,5), (7,5), (8,5), (9,5)]))

def main():
    global SCREEN, CLOCK, FOOD_LOC
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_HEIGHT, WINDOW_WIDTH))
    CLOCK = pygame.time.Clock()
    generateFood()


    while True:
        draw()
        
        if not gameOver():
            # Move all snakes
            for snake in SNAKES:
                snake.move()
        else:
            drawGameEndPanel()

        # Handle key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        CLOCK.tick(GAME_SPEED)

# Draws window contents
def draw():
    #### Grid
    SCREEN.fill(TILE_COLOR)

    for x in range(WINDOW_WIDTH//BLOCK_SIZE):
        for y in range(WINDOW_HEIGHT//BLOCK_SIZE):
            rect = pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE,
                            BLOCK_SIZE, BLOCK_SIZE)
            if BOARD[y][x] == None:
                pygame.draw.rect(SCREEN, BODY_COLOR, rect, 1)
            else:
                pygame.draw.rect(SCREEN, BODY_COLOR, rect)

    #### Snakes
    for snake in SNAKES:
        # Body
        for x,y in snake.position:
            rect = pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE,
                                BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(SCREEN, BODY_COLOR, rect)
        # Head
        rect = pygame.Rect(snake.position[-1][0]*BLOCK_SIZE, snake.position[-1][1]*BLOCK_SIZE,
                            BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(SCREEN, HEAD_COLOR, rect)

    #### Food
    rect = pygame.Rect(FOOD_LOC[0]*BLOCK_SIZE, FOOD_LOC[1]*BLOCK_SIZE,
                                BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(SCREEN, FOOD_COLOR, rect)

def drawGameEndPanel():
    myfont = pygame.font.SysFont("monospace", 40)
    label = myfont.render("GAME OVER!", 1, (0,0,0), (245,245,245))
    SCREEN.blit(label, (BOARD_WIDTH*BLOCK_SIZE//2 - 120, BOARD_HEIGHT*BLOCK_SIZE//2 - 20))

def generateFood():
    global FOOD_LOC
    options = []
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            if BOARD[y][x] == None:
                options.append((x,y))
    food_loc = random.choice(options)

    BOARD[food_loc[1]][food_loc[0]] = 0

    FOOD_LOC = food_loc

# Cheks if any snakes have overlapping bodyparts
def gameOver():
    bodies = reduce(lambda a,b: a+b, [snake.position for snake in SNAKES])
    return len(bodies) != len(set(bodies)) 

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    main()
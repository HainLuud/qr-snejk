import pygame
import random
import sys
from Node import Node
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
UP, DOWN, LEFT, RIGHT = ((0,-1), (0,1), (-1,0), (1,0))


class Snake:
    def __init__(self, id, position, moveDecider = "random"):
        self.id = id
        
        self.lastDirection = (position[-1][0]-position[-2][0], position[-1][1]-position[-2][1])
        # List where, position[0] == tail, position[-1] == head
        self.position = position
        for pos in position:
            BOARD[pos[1]][pos[0]] = id
        
        # Function which gets called when the snake needs to make a move.
        if moveDecider == "random":
            self.moveDecider = self.randomMove
        elif moveDecider == "ai":
            self.moveDecider = self.aiMove
        elif moveDecider == "qr":
            self.moveDecider = self.qrMove
        
    # All possible moves for snake, that, dont hit itself.
    def possibleMoves(self, startPos):
        moves = []
        # Array of all occupied positions
        occupied = SNAKES[0].position + SNAKES[1].position

        for move in (UP, DOWN, LEFT, RIGHT):
            frm = startPos
            new_x = (frm[0] + move[0]) % BOARD_WIDTH
            new_y = (frm[1] + move[1]) % BOARD_HEIGHT

            """
            # Väldib iseendale otsa sõitmist
            if BOARD[new_y][new_x] != self.id:
                moves.append(move)
            """
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

    # Return node with updated distances from starNode, endNode and the f-score using Manhattan Distance
    def setNodeDistances(self, node, start, end):
        node.g = abs(node.position[0] - start.position[0]) + abs(node.position[1] - start.position[1])
        node.h = abs(node.position[0] - end.position[0]) + abs(node.position[1] - end.position[1])
        node.f = node.g + node.h
        return node

    def add_to_open(self, open, neighbor):
        for node in open:
            if (neighbor == node and neighbor.f >= node.f):
                return False
        return True
    # AI loogika, peab tagastama ühe võimalustest [UP, DOWN, LEFT, RIGHT]
    def aiMove(self):
        # Code influence from https://www.annytab.com/a-star-search-algorithm-in-python/

        openNodes = []
        closedNodes = []

        startNode = Node(self.position[-1], None, None) # head location
        endNode = Node(FOOD_LOC, None, None)

        openNodes.append(startNode)
        lastMove = None
        while len(openNodes) != 0:
            # Use list as a priority queue
            openNodes.sort()
            currentNode = openNodes.pop(0)
            closedNodes.append(currentNode)
            
            if currentNode == endNode:
                while currentNode != startNode:
                    prevNode = currentNode
                    currentNode = currentNode.parent
                return prevNode.moveMade
            
            for move in self.possibleMoves(currentNode.position):
                neighbor = Node((currentNode.position[0] + move[0], 
                                currentNode.position[1] + move[1]), currentNode, move)
            
                if neighbor in closedNodes:
                    continue
                
                neighbor =  self.setNodeDistances(neighbor, startNode, endNode)

                if (self.add_to_open(openNodes, neighbor)):
                    openNodes.append(neighbor)     
        
        # Return random move, if no path could be found
        print("still picked random  ¯\_(ツ)_/¯")
        return self.randomMove()

    
    # QR loogika, peab tagastama ühe võimalustest [UP, DOWN, LEFT, RIGHT]
    def qrMove(self):

        return self.randomMove()

    # Moves the snake based on its moveDecider
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


def main():
    global SCREEN, CLOCK, FOOD_LOC, SNAKES
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_HEIGHT, WINDOW_WIDTH))
    CLOCK = pygame.time.Clock()
    generateFood()

    # Usside loomine
    # AI
    SNAKES.append(Snake(1, [(1,1), (2,1), (3,1), (4,1), (5,1)], "ai"))
    # QR
    SNAKES.append(Snake(2, [(5,5), (6,5), (7,5), (8,5), (9,5)], "qr"))

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
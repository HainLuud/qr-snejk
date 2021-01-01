import pygame
import random
import sys
from Node import Node
from functools import reduce
import numpy as np
import qr_reader as qr
from enum import Enum

###################### BOARD/WINDOW ######################
# Colours
TILE_COLOR = (50, 50, 50)
GRID_COLOR = (245, 245, 245)
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
GAME_SPEED = 3
# Tilt sensitivity. When player tilts the QR code at {TILT_SENSITIVITY} degrees the
# snake will change direction (according to the direction of the tilt).
TILT_SENSITIVITY = 10
###################### SNAKE ######################
# On the next move snakes head will be moved by (x, y)
NUMBER_OF_SNAKES = None
UP, DOWN, LEFT, RIGHT = ((0,-1), (0,1), (-1,0), (1,0))



class Snake:
    def __init__(self, id, position, moveDecider = "random"):
        self.id = id
        self.head_color, self.body_color = generateColor()
         
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

    # Return node with updated distances from starNode, endNode and the f-score using Manhattan Distance
    def setNodeDistances(self, node, start, end):
        node.g = abs(node.position[0] - start.position[0]) + abs(node.position[1] - start.position[1])
        node.h = abs(node.position[0] - end.position[0]) + abs(node.position[1] - end.position[1])
        node.f = node.g + node.h
        return node

    def openDoesntContain(self, open, neighbor):
        for node in open:
            if (neighbor == node and neighbor.f >= node.f):
                return False
        return True

    # AI loogika, peab tagastama ühe võimalustest [UP, DOWN, LEFT, RIGHT]
    def aiMove(self):
        # Influence from https://www.annytab.com/a-star-search-algorithm-in-python/

        openNodes = []
        closedNodes = []

        startNode = Node(self.position[-1], None, None) # head location node
        endNode = Node(FOOD_LOC, None, None) # food location node

        openNodes.append(startNode)
        lastMove = None
        while len(openNodes) != 0:
            # Use list as a priority queue and retrieve the node with the lowest f-score
            openNodes.sort()
            currentNode = openNodes.pop(0)
            closedNodes.append(currentNode)
            
            # If the selected node is where we wanted to go then 
            if currentNode == endNode:
                # retrace our steps back to the initial step that led us here and return it
                while currentNode != startNode:
                    prevNode = currentNode
                    currentNode = currentNode.parent
                return prevNode.moveMade
            
            # Else, go through all possible moves the snake could make from the node
            for move in self.possibleMoves(currentNode.position):
                # calculate what the g, h and f scores of that move would be
                new_x = (currentNode.position[0] + move[0]) % BOARD_WIDTH
                new_y = (currentNode.position[1] + move[1]) % BOARD_HEIGHT
                neighbor = Node((new_x, new_y), currentNode, move)

                if neighbor in closedNodes:
                    continue
                
                neighbor =  self.setNodeDistances(neighbor, startNode, endNode)

                # and if it isn't already in our list of places to look at, then add it 
                if (self.openDoesntContain(openNodes, neighbor)):
                    openNodes.append(neighbor)     
        
        # Return random move, if no path could be found
        return self.randomMove()
    
    # QR loogika, peab tagastama ühe võimalustest [UP, DOWN, LEFT, RIGHT]
    def qrMove(self):
        tilt = qr.getMostSignificantTilt()
        qr.resetMostSignificantTilt()
        print(tilt)
        if abs(tilt) > TILT_SENSITIVITY:
            directions = (UP, RIGHT, DOWN, LEFT)  # directions in clockwise order
            return directions[int((directions.index(self.lastDirection) - tilt // abs(tilt)) % len(directions))]
        return self.lastDirection


    # Moves the snake based on its moveDecider
    def move(self):
        direction = self.moveDecider()
        self.lastDirection = direction
        head = self.position[-1]
        reward = -0.5

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
            reward = 100
        else:
            tail = self.position.pop(0)
    	
        # BOARD changes 
        # Adds new head to board
        BOARD[new_head[1]][new_head[0]] = self.id
        # Removes tail from board
        BOARD[tail[1]][tail[0]] = None
        return BOARD, reward, gameOver(), direction

class GameState(Enum):
    CALIBRATION = 0
    SELECT_NUMBER_OF_SNAKES = 1
    SELECT_SNAKE_1 = 2
    SELECT_SNAKE_2 = 3
    RUNNING = 4
    END_SCREEN = 5

def generateTrainData():
    global SCREEN, CLOCK, FOOD_LOC, SNAKES
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_HEIGHT, WINDOW_WIDTH))
    pygame.display.set_caption('QR-Snek')

    CLOCK = pygame.time.Clock()
    generateFood()
    training_data = []
    scores = []
    goodGameScores = []

    # For 1000 games
    for i in range(1000): 
        print("Game", i, ". of 1000")
        snek = Snake(3, [(1,11), (1,12), (1,13), (1,14), (1,15)], "random")
        del SNAKES[:]
        SNAKES.append(snek)

        score = 100
        # moves specifically from this environment:
        gameMemory = []
        # previous board that we saw
        prevState = []

        # for 300 steps each game
        for j in range(300):
            board, reward, gameOver, move = snek.move()
            drawGame()
            pygame.display.update()
            CLOCK.tick(GAME_SPEED)

            gameMemory.append([prevState, move])
            prevState = board
            score += reward
            if gameOver: break

        if score >= 100:
            goodGameScores.append(score)
            for data in gameMemory:
                # convert move to one-hot (output for NN)
                moveToOneHot = {UP:[0, 0, 0, 1], DOWN:[0, 0, 1, 0], LEFT:[0, 1, 0, 0], RIGHT:[1, 0, 0, 0] }
                # saving our training data
                training_data.append([data[0], moveToOneHot[data[1]]])

        # save overall scores
        scores.append(score)

    # some stats here, to further illustrate the neural network magic!
    from statistics import median, mean
    print('Average accepted score:', mean(goodGameScores))
    print('Median score for accepted scores:', median(goodGameScores))

    # just in case you wanted to reference later
    training_data_save = np.array(training_data)
    np.save('saved.npy', training_data_save)

    return training_data

def handleKeyPress():
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 1
                elif event.key == pygame.K_2:
                    return 2
                elif event.key == pygame.K_RETURN:
                    return 3

# All the snakes will be stored in array
SNAKES = []

def main():
    global SCREEN, CLOCK, FOOD_LOC, SNAKES
    pygame.init()
    qr.init()
    SCREEN = pygame.display.set_mode((WINDOW_HEIGHT, WINDOW_WIDTH))
    pygame.display.set_caption('QR-Snek')

    CLOCK = pygame.time.Clock()
    generateFood()

    # Game loop
    GAME_STATE = GameState.CALIBRATION
    while True:
        if GAME_STATE == GameState.CALIBRATION:
            drawCalbrationScreen()
            key = handleKeyPress()
            if key:
                GAME_STATE = GameState.SELECT_NUMBER_OF_SNAKES

        elif GAME_STATE == GameState.SELECT_NUMBER_OF_SNAKES:
            drawStartScreen()
            key = handleKeyPress()
            if key:
                NUMBER_OF_SNAKES = key
                GAME_STATE = GameState.SELECT_SNAKE_1

        elif GAME_STATE == GameState.SELECT_SNAKE_1:
            drawSelectSnakeScreen("first")
            key = handleKeyPress()
            if key:
                snake_type = key
                if key == 1:
                    SNAKES.append(Snake(1, [(1,1), (2,1), (3,1), (4,1), (5,1)], "ai"))
                elif key == 2:
                    SNAKES.append(Snake(1, [(1,1), (2,1), (3,1), (4,1), (5,1)], "qr"))

                if NUMBER_OF_SNAKES == 1:
                    GAME_STATE = GameState.RUNNING
                elif NUMBER_OF_SNAKES == 2:
                    GAME_STATE = GameState.SELECT_SNAKE_2

        elif GAME_STATE == GameState.SELECT_SNAKE_2:
            drawSelectSnakeScreen("second")
            key = handleKeyPress()
            if key:
                snake_type = key
                if key == 1:
                    SNAKES.append(Snake(1, [(5,5), (6,5), (7,5), (8,5), (9,5)], "ai"))
                elif key == 2:
                    SNAKES.append(Snake(1, [(5,5), (6,5), (7,5), (8,5), (9,5)], "qr"))

                GAME_STATE = GameState.RUNNING

        elif GAME_STATE == GameState.RUNNING:
            # Move all snakes
            for snake in SNAKES:
                snake.move()
            drawGame()

            handleKeyPress()
            if gameOver():
                GAME_STATE = GameState.END_SCREEN
        
        else:
            drawEndScreen()
            break

        pygame.display.update()
        CLOCK.tick(GAME_SPEED)

# Draws window contents
def drawGame():
    #### Grid
    SCREEN.fill(TILE_COLOR)

    for x in range(WINDOW_WIDTH//BLOCK_SIZE):
        for y in range(WINDOW_HEIGHT//BLOCK_SIZE):
            rect = pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE,
                            BLOCK_SIZE, BLOCK_SIZE)
            if BOARD[y][x] == None:
                pygame.draw.rect(SCREEN, GRID_COLOR, rect, 1)
            else:
                pygame.draw.rect(SCREEN, GRID_COLOR, rect)

    #### Snakes
    for snake in SNAKES:
        # Body
        for x,y in snake.position:
            rect = pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE,
                                BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(SCREEN, snake.body_color, rect)
        # Head
        rect = pygame.Rect(snake.position[-1][0]*BLOCK_SIZE, snake.position[-1][1]*BLOCK_SIZE,
                            BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(SCREEN, snake.head_color, rect)

    #### Food
    rect = pygame.Rect(FOOD_LOC[0]*BLOCK_SIZE, FOOD_LOC[1]*BLOCK_SIZE,
                                BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(SCREEN, FOOD_COLOR, rect)


def drawCalbrationScreen():
    SCREEN.fill(TILE_COLOR)
    myfont = pygame.font.SysFont("monospace", 12)
    label1 = myfont.render("QR detector calibration.", 1, (0,0,0), (245,245,245))
    label2 = myfont.render("Camera works best with QR code printed on paper.", 1, (0,0,0), (245,245,245))
    label3_1 = myfont.render("If you choose to use a secondary screen to show QR code", 1, (0,0,0), (245, 245, 245))
    label3_2 = myfont.render("to camera then adjust your screen's brightness so that", 1, (0,0,0), (245,245,245))
    label3_3 = myfont.render("the camera can detect the QR code better.", 1, (0,0,0), (245,245,245))
    label4 = myfont.render("When done calibrating press ENTER to continue.", 1, (0, 0, 0), (245, 245, 245))
    SCREEN.blit(label1, (0, 0))
    SCREEN.blit(label2, (0, 30))
    SCREEN.blit(label3_1, (0, 60))
    SCREEN.blit(label3_2, (0, 80))
    SCREEN.blit(label3_3, (0, 100))
    SCREEN.blit(label4, (0, 130))


def drawStartScreen():
    SCREEN.fill(TILE_COLOR)
    myfont = pygame.font.SysFont("monospace", 18)
    label1 = myfont.render("Pick the game format by pressing", 1, (0,0,0), (245,245,245))
    label2 = myfont.render("on the number:", 1, (0,0,0), (245,245,245))
    SCREEN.blit(label1, (0, 0))
    SCREEN.blit(label2, (0, 20))

    label3 = myfont.render("1 - 1 snake", 1, (0,0,0), (245,245,245))
    label4 = myfont.render("2 - 2 snakes", 1, (0,0,0), (245,245,245))
    SCREEN.blit(label3, (0, 60))
    SCREEN.blit(label4, (0, 80))

def drawSelectSnakeScreen(snake_nr):
    SCREEN.fill(TILE_COLOR)
    myfont = pygame.font.SysFont("monospace", 18)
    label1 = myfont.render("Pick {} snake".format(snake_nr), 1, (0,0,0), (245,245,245))
    SCREEN.blit(label1, (0, 0))

    label3 = myfont.render("1 - 1 A*", 1, (0,0,0), (245,245,245))
    label4 = myfont.render("2 - 2 QR reader", 1, (0,0,0), (245,245,245))
    SCREEN.blit(label3, (0, 40))
    SCREEN.blit(label4, (0, 60))

def drawEndScreen():
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

# Generates head and body color for the snake
def generateColor():
    head_color = [random.randint(150,220),0,0] 
    random.shuffle(head_color)
    
    # Every color value gets 
    body_color = [min(255, x + int((255-x)/1.4)) for x in head_color.copy()]


    #return ((20,20,20), (245,245,245))
    return head_color, body_color

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    main()
    #train_data = generateTrainData()

    #f = np.load("saved.npy", allow_pickle=True)
    #print(f)
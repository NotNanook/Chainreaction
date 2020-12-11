import pygame
import sys
import os
import time
import warnings
warnings.filterwarnings("ignore")

from math import *
from copy import deepcopy


class Color():
    """
    Class for all used colors
    """
    background = (21, 67, 96)
    border = (208, 211, 212)
    red = (231, 76, 60)
    white = (244, 246, 247)
    violet = (136, 78, 160)
    yellow = (244, 208, 63)
    green = (88, 214, 141)

class Spot():
    """
    A class for every valid point on the board
    """
    def __init__(self):
        self.color = Color.border
        self.neighbors = []
        self.numAtoms = 0
        self.neighbourOffsets = [(-1, 0), (1, 0), (0, -1), (0,1)]

    def addNeighbors(self, i, j, game):

        # go over every offset and check if its a valid neighbour
        for offset in self.neighbourOffsets:
            try:
                # checking if coords are valid
                if (i + offset[0] in range(0, game.rows) and j + offset[1] in range(0, game.cols)) and game.grid[i + offset[0]][j + offset[1]] != game.INVALID:
                    self.neighbors.append(game.grid[i + offset[0]][j + offset[1]])

            except IndexError:
                continue

class Game():
    """
    Chainreaction main game class
    """
    def __init__(self):

        self.INVALID = -1

        self.cellSize = 60
        self.rows = 0                       # 0 as default value until further initialized
        self.cols = 0                       # 0 as default value until further initialized
        self.d = self.cellSize // 2 - 2

        self.WIDTH = 0                      # 0 as default value until further initialized
        self.HEIGHT = 0                     # 0 as default value until further initialized

        self.player = 0
        self.winner = None

        self.grid = []

        self.color = [(Color.red), (Color.green)]

        self.vibrate = 0.5

        self.turns = 0

        self.winner = None
        self.end = False

        self.clock = pygame.time.Clock()

        self.drawDelay = 0.5

    def getState(self):
        # Get tuple of the state of the board. Used for AI mostly

        state = deepcopy(self.grid)
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if state[i][j] != self.INVALID:
                    state[i][j] = (state[i][j].numAtoms, state[i][j].color)

        for i in range(len(state)):
            state[i] = tuple(state[i])

        return state

    def switch_player(self):
        # Switch player whos turn it is

        self.player = Game.other_player(self.player)

    def initializeGrid(self, rows, cols, board="normal"):
        # Initialize the game board

        self.board = board
        self.rows = rows
        self.cols = cols

        self.WIDTH = self.cols * self.cellSize  + 1
        self.HEIGHT = self.rows * self.cellSize + 1

        # check which game board type it is
        if board == "normal":
            self.grid = [[0 for i in range(self.cols)] for _ in range(self.rows)]

        elif board == "tree":
            self.grid = [[-1, -1, -1,  0,  0, -1, -1, -1],
                         [-1, -1,  0,  0,  0,  0, -1, -1],
                         [-1,  0,  0,  0,  0,  0,  0, -1],
                         [-1,  0,  0,  0,  0,  0,  0, -1],
                         [-1, -1, -1,  0,  0, -1, -1, -1],
                         [-1, -1, -1,  0,  0, -1, -1, -1],
                         [-1, -1, -1,  0,  0, -1, -1, -1],
                         [-1, -1, -1,  0,  0, -1, -1, -1],
                         [-1, -1, -1,  0,  0, -1, -1, -1]]

        elif board == "circle":
            self.grid = [[-1, -1, -1, -1, -1, -1, -1, -1],
                         [-1, -1, -1,  0,  0, -1, -1, -1],
                         [-1, -1,  0,  0,  0,  0, -1, -1],
                         [-1,  0,  0,  0,  0,  0,  0, -1],
                         [-1,  0,  0,  0,  0,  0,  0, -1],
                         [-1, -1,  0,  0,  0,  0, -1, -1],
                         [-1, -1, -1,  0,  0, -1, -1, -1],
                         [-1, -1, -1, -1, -1, -1, -1, -1],
                         [-1, -1, -1, -1, -1, -1, -1, -1]]

        else:
            # If given board name is not defined, raise error
            raise NotImplementedError

        # Populate the grid with cls.spots
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] != self.INVALID:
                    newObj = Spot()
                    self.grid[i][j] = newObj

        # Add all possible neighbours to a cell
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] != self.INVALID:
                    self.grid[i][j].addNeighbors(i, j, self)


    def addAtom(self, y, x, color, display=None, ai=False):
        # Add atom to clicked cell

        self.grid[y][x].numAtoms += 1
        self.grid[y][x].color = color
        if self.grid[y][x].numAtoms >= len(self.grid[y][x].neighbors):
            self.overFlow(self.grid[y][x], color, display, 1, ai)

    def overFlow(self, cell, color, display, recursion, ai=False):
        # Overflow cell and overflow others if neccessary

        if ai == False:
            self.showPresentGrid(display)

        cell.numAtoms = 0
        for m in range(len(cell.neighbors)):
            cell.neighbors[m].numAtoms += 1
            cell.neighbors[m].color = color
            if cell.neighbors[m].numAtoms >= len(cell.neighbors[m].neighbors) and recursion < 50:
                recursion += 1
                self.overFlow(cell.neighbors[m], color, display, recursion, ai)

    def drawGrid(self, display):
        # Display grid

        x = 0
        y = 0

        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != self.INVALID:
                    pygame.draw.rect(display, self.color[self.player], (x, y, self.cellSize, self.cellSize), 2)

                x += self.cellSize

            x = 0
            y += self.cellSize

    def showPresentGrid(self, display, vibrate = 1):
        # Display all atoms. Can be treated as a black box

        r = -self.cellSize
        c = -self.cellSize
        padding = 2
        for i in range(self.rows):
            r += self.cellSize
            c = -self.cellSize

            for j in range(self.cols):
                c += self.cellSize
                if self.grid[i][j] != self.INVALID and self.grid[i][j].numAtoms == 0:
                    self.grid[i][j].color = Color.border

                elif self.grid[i][j] != self.INVALID and self.grid[i][j].numAtoms == 1:
                    pygame.draw.ellipse(display, self.grid[i][j].color, (c + self.cellSize/2 - self.d/2, r + self.cellSize/2 - self.d/2 + vibrate, self.d, self.d))

                elif self.grid[i][j] != self.INVALID and self.grid[i][j].numAtoms == 2:
                    pygame.draw.ellipse(display, self.grid[i][j].color, (c + 5, r + self.cellSize/2 - self.d/2 - vibrate, self.d, self.d))
                    pygame.draw.ellipse(display, self.grid[i][j].color, (c + + self.d/2 + self.cellSize/2 - self.d/2 + vibrate, r + self.d/2, self.d, self.d))

                elif self.grid[i][j] != self.INVALID and self.grid[i][j].numAtoms == 3:
                    angle = 90
                    x = r + (self.d/2)*cos(radians(angle)) + self.cellSize/2 - self.d/2
                    y = c + (self.d/2)*sin(radians(angle)) + self.cellSize/2 - self.d/2
                    pygame.draw.ellipse(display, self.grid[i][j].color, (y - vibrate, x, self.d, self.d))
                    x = r + (self.d/2)*cos(radians(angle + 90)) + self.cellSize/2 - self.d/2
                    y = c + (self.d/2)*sin(radians(angle + 90)) + 5
                    pygame.draw.ellipse(display, self.grid[i][j].color, (y + vibrate, x, self.d, self.d))
                    x = r + (self.d/2)*cos(radians(angle - 90)) + self.cellSize/2 - self.d/2
                    y = c + (self.d/2)*sin(radians(angle - 90)) + 5
                    pygame.draw.ellipse(display, self.grid[i][j].color, (y - vibrate, x, self.d, self.d))

        pygame.display.update()

    def isnotEnd(self):
        # Checks if game hasnt ended yet

        colorsFound = set()
        for column in self.grid:
            for row in column:
                if row != self.INVALID and row.color != Color.border:
                    colorsFound.add(row.color)

        if len(colorsFound) <= 1 and self.turns > 2:
            return False
        return True

    def reset(self, game):
        # Reset the game board

        self.initializeGrid(game.rows, game.cols, game.board)
        self.player = 0
        self.end = False
        self.winner = None
        self.turns = 0

    @classmethod
    def available_actions(cls, state, color):
        # Get list of all available action. Used for AI mostly

        actions = []

        for row in range(len(state)):
            for col in range(len(state[row])):
                if state[row][col] != -1 and (state[row][col][1] == Color.border or state[row][col][1] == color):
                    actions.append((row, col))

        return actions

    @classmethod
    def other_player(cls, player):
        # Get other player number

        return 0 if player == 1 else 1

def play(game):
    # an example of a game loop

    display = pygame.display.set_mode((game.WIDTH, game.HEIGHT))

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    time1 = time.time()
                    game.reset(game)

            elif event.type == pygame.MOUSEBUTTONDOWN and not game.end and game.player == 0:
                time1 = time.time()
                x, y = pygame.mouse.get_pos()
                i = y//game.cellSize
                j = x//game.cellSize
                if game.grid[i][j] != game.INVALID and (game.grid[i][j].color == game.color[game.player] or game.grid[i][j].color == Color.border):
                    game.addAtom(i, j, game.color[game.player], display)
                    game.turns += 1

                    game.switch_player()

            elif event.type == pygame.MOUSEBUTTONDOWN and not game.end and game.player == 1:
                time1 = time.time()
                x, y = pygame.mouse.get_pos()
                i = y//game.cellSize
                j = x//game.cellSize
                if game.grid[i][j] != game.INVALID and (game.grid[i][j].color == game.color[game.player] or game.grid[i][j].color == Color.border):
                    game.addAtom(i, j, game.color[game.player], display)
                    game.turns += 1

                    game.switch_player()

        if not game.isnotEnd() and not game.end:
            game.winner = game.other_player(game.player)
            game.end = True
            print("The winner is", str(game.winner))

        display.fill(Color.background)

        game.vibrate *= -1

        game.drawGrid(display)
        game.showPresentGrid(display, game.vibrate)
        pygame.display.update()

        game.clock.tick(20)

if __name__ ==  "__main__":
    game = Game()
    game.initializeGrid(9, 8, board="circle")
    play(game)

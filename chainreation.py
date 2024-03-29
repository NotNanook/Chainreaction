import pygame
import sys
import os
import time
import warnings
warnings.filterwarnings("ignore")

from math import *
from copy import deepcopy
from pygame import gfxdraw

class Color():
    """
    Class for all used colors
    """
    background = (22, 22, 22)
    border = (0, 0, 0)
    red = (200, 75, 49)
    green = (52, 103, 81)

class Spot():
    """
    A class for every valid point on the board
    """
    def __init__(self):
        self.color = Color.border
        self.numAtoms = 0
        self.neighbours = []
        self.neighbourCount = 0
        self.neighbourOffsets = [(-1, 0), (1, 0), (0, -1), (0,1)]

    def __str__(self):
        return "Color:" + str(self.color) + " Atoms: " + str(self.numAtoms)

    def addNeighbours(self, i, j, game):

        # go over every offset and check if its a valid neighbour
        for offset in self.neighbourOffsets:
            try:
                # checking if coords are valid
                if (i + offset[0] in range(0, game.rows) and j + offset[1] in range(0, game.cols)) and game.grid[i + offset[0]][j + offset[1]] != game.INVALID:
                    self.neighbours.append(game.grid[i + offset[0]][j + offset[1]])

            except IndexError:
                continue

        self.neighbourCount = len(self.neighbours)

class Game():
    """
    Chainreaction main game class
    """
    def __init__(self):

        self.display = None
        
        self.INVALID = -1

        self.cellSize = 80
        self.cellthickness = 6
        self.rows = 0                       # 0 as default value until further initialized
        self.cols = 0                       # 0 as default value until further initialized
        self.r = self.cellSize // 2 - 20

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

        self.overflowList = [] 
        self.lastOverflowTime = time.time_ns()

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

    def initializeGrid(self, board, rows=9, cols=8):
        self.board = board
        self.rows = rows
        self.cols = cols

        self.WIDTH = self.cols * self.cellSize - (self.cols-1)*self.cellthickness # (self.cols-1)*self.cellthickness is to compensate for border thickness
        self.HEIGHT = self.rows * self.cellSize - (self.rows-1)*self.cellthickness # (self.rows-1)*self.cellthickness is to compensate for border thickness

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
                    self.grid[i][j].addNeighbours(i, j, self)

    def addAtom(self, y, x, color):
        self.grid[y][x].numAtoms += 1
        self.grid[y][x].color = color
        if self.grid[y][x].numAtoms >= len(self.grid[y][x].neighbours):
            self.overFlow(self.grid[y][x], color)

    def overFlow(self, cell, color):
        localOverflowList = []
        cell.numAtoms = 0
        for neighbour in cell.neighbours:
            neighbour.numAtoms += 1
            neighbour.color = color
            if neighbour.numAtoms >= len(neighbour.neighbours):
                localOverflowList.append(neighbour)

        if localOverflowList != []:
            self.overflowList.append(localOverflowList)

    def handleOverflowList(self):
        if len(self.overflowList) >= 1:
            for cell in self.overflowList[0]:          # Order of simulation is important (buggy)
                self.overFlow(cell, cell.color)
            self.overflowList.pop(0)
            self.lastOverflowTime = time.time_ns()

    def drawGrid(self):
        x = 0
        y = 0

        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != self.INVALID:
                    pygame.draw.rect(self.display, self.color[self.player], (x, y, self.cellSize, self.cellSize), self.cellthickness)

                x += self.cellSize - self.cellthickness

            x = 0
            y += self.cellSize - self.cellthickness

    def showPresentGrid(self, vibrate = 1):
        yPos = -self.cellSize + self.cellthickness
        xPos = -self.cellSize + self.cellthickness

        for i in range(self.rows):
            yPos += self.cellSize - self.cellthickness
            xPos = -self.cellSize + self.cellthickness

            for j in range(self.cols):
                realVibrate = 0
                xPos += self.cellSize - self.cellthickness
                if self.grid[i][j] != self.INVALID and self.grid[i][j].numAtoms == 0:
                    self.grid[i][j].color = Color.border

                elif self.grid[i][j] != self.INVALID and self.grid[i][j].numAtoms == 1:
                    if self.grid[i][j].neighbourCount == 2:
                        realVibrate = vibrate

                    drawCircle(self.display, self.grid[i][j].color, xPos + self.cellSize/2, yPos + self.cellSize/2 + realVibrate, self.r)

                elif self.grid[i][j] != self.INVALID and self.grid[i][j].numAtoms == 2:
                    if self.grid[i][j].neighbourCount == 3:
                        realVibrate = vibrate

                    drawCircle(self.display, self.grid[i][j].color, xPos + self.cellSize/2 + self.r/1.5, yPos - realVibrate + self.cellSize/2, self.r)
                    drawCircle(self.display, self.grid[i][j].color, xPos + self.cellSize/2 - self.r/1.5 + realVibrate, yPos - realVibrate + self.cellSize/2, self.r)

                elif self.grid[i][j] != self.INVALID and self.grid[i][j].numAtoms == 3:
                    if self.grid[i][j].neighbourCount == 4:
                        realVibrate = vibrate

                    x = xPos + self.cellSize/2 + self.r/1.5
                    y = yPos + self.cellSize/2
                    drawCircle(self.display, self.grid[i][j].color, x, y - vibrate, self.r)

                    x = xPos + self.cellSize/2 - self.r/1.5
                    y = yPos + self.cellSize/2 + self.r/1.5
                    drawCircle(self.display, self.grid[i][j].color, x, y + vibrate, self.r)

                    x = xPos + self.cellSize/2 - self.r/1.5
                    y = yPos + self.cellSize/2 - self.r/1.5
                    drawCircle(self.display, self.grid[i][j].color, x + vibrate, y - vibrate, self.r)

    def justEnded(self):
        colorsFound = set()
        for column in self.grid:
            for row in column:
                if row != self.INVALID and row.color != Color.border:
                    colorsFound.add(row.color)

        if len(colorsFound) <= 1 and self.turns > 2 and not self.end:
            return True
        return False

    def reset(self, game):
        self.initializeGrid(game.board, game.rows, game.cols)
        self.player = 0
        self.end = False
        self.winner = None
        self.turns = 0

def drawCircle(surface, color, x, y, radius):
    # Draw antialiased circle because i dont like sprites
    x, y = int(x), int(y)
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)

def play(game):
    game.display = pygame.display.set_mode((game.WIDTH, game.HEIGHT))
    pygame.display.set_caption("Chainreaction")

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    time1 = time.time()
                    game.reset(game)

            if not game.end and len(game.overflowList) == 0:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    time1 = time.time()
                    x, y = pygame.mouse.get_pos()
                    i = y//(game.cellSize - game.cellthickness)
                    j = x//(game.cellSize - game.cellthickness)
                    if game.grid[i][j] != game.INVALID and (game.grid[i][j].color == game.color[game.player] or game.grid[i][j].color == Color.border):
                        game.addAtom(i, j, game.color[game.player])
                        game.turns += 1

                        game.switch_player()

        if game.justEnded():
            game.winner = game.other_player(game.player)
            game.end = True
            print("The winner is", str(game.winner))

        game.vibrate *= -1

        if time.time_ns() - game.lastOverflowTime >= 90000000:
            game.handleOverflowList()

        game.display.fill(Color.background)
        game.drawGrid()
        game.showPresentGrid(game.vibrate)

        pygame.display.update()
        game.clock.tick(60)

if __name__ ==  "__main__":
    game = Game()
    game.initializeGrid("normal")
    play(game)
import time
import random
import shelve
import pickle
import os
import pdb

import cellular
import imp
# import winsound
imp.reload(cellular)
from qlearn_mod_random import QLearn
import qlearn_mod_random as qlearn # to use the alternative exploration method
#import qlearn # to use standard exploration method
imp.reload(qlearn)



directions = 8

lookdist = 8
lookcells = []
for i in range(-lookdist,lookdist+1):
    for j in range(-lookdist,lookdist+1):
        if (abs(i) + abs(j) <= lookdist) and (i != 0 or j != 0):
            lookcells.append((i,j))

def pickRandomLocation():
    while 1:
        x = random.randrange(world.width)
        y = random.randrange(world.height)
        cell = world.getCell(x, y)
        if not (cell.wall or len(cell.agents) > 0):
            return cell

class Cell(cellular.Cell):
    wall = False
    # @property
    # def colour(self):
    #         """I'm the 'colour' property."""
    #         if self.wall:
    #           return 'black'
    #         else:
    #           return 'white'
    #         return self._colour

    def colour(self):
        if self.wall:
            return 'black'
        else:
            return 'white'
    def load(self, data):
                        # self.display.redrawCell(a.cell.x, a.cell.y)
        if data == 'X':
            self.wall = True
        else:
            self.wall = False

class Cat(cellular.Agent):
    cell = None
    score = 0
    colour = 'orange'
    img = "cat.png"

    def update(self):
        cell = self.cell
        if cell != mouse.cell:
            self.goTowards(mouse.cell)
            while cell == self.cell:
                self.goInDirection(random.randrange(directions))

class Cheese(cellular.Agent):
    colour = 'yellow'
    img = "cheese.png"
    def update(self):
        pass

class Mouse(cellular.Agent):
    colour = 'blue'
    img = "mouse.png"
    def __init__(self):
        self.ai = None
        self.ai = qlearn.QLearn(actions=list(range(directions)),
                                alpha=0.2, gamma=0.9, epsilon=0.1)
        self.eaten = 0
        self.fed = 0
        self.lastState = None
        self.lastAction = None
    def update(self):
        # calculate the state of the surrounding cells
        state = self.calcState()
        # asign a reward of -1 by default
        reward = -1
        # observe the reward and update the Q-value
        if self.cell == cat.cell:
            self.eaten += 1
            reward = -100
            if QLearn.useSound:
                print("Winsound ki jagah")
                # winsound.PlaySound('cat.wav', winsound.SND_FILENAME)
            if self.lastState is not None:
                self.ai.learn(self.lastState, self.lastAction, reward, state)
            #restart
            self.lastState = None
            self.cell = pickRandomLocation()
            return
        if self.cell == cheese.cell:
            self.fed += 1
            reward = 50
            if QLearn.useSound:

                print("Winsound ki jagah")
                # winsound.PlaySound('snd1.wav', winsound.SND_FILENAME)
            #new cheese at random loc
            cheese.cell = pickRandomLocation()

        if self.lastState is not None:
            self.ai.learn(self.lastState, self.lastAction, reward, state)

        # Choose a new action and execute it
        state = self.calcState()
        print(state)
        action = self.ai.chooseAction(state)
        self.lastState = state
        self.lastAction = action
        self.goInDirection(action)

    def calcState(self):
        def cellvalue(cell):
            if cat.cell is not None and (cell.x == cat.cell.x and
                                         cell.y == cat.cell.y):
                return 3
            elif cheese.cell is not None and (cell.x == cheese.cell.x and
                                              cell.y == cheese.cell.y):
                return 2
            else:
                return 1 if cell.wall else 0

        return tuple([cellvalue(self.world.getWrappedCell(self.cell.x + j, self.cell.y + i))
                      for i,j in lookcells])
mouse = Mouse()
cat = Cat()
cheese = Cheese()

world = cellular.World(Cell, directions=directions, filename=r'waco.txt')
world.age = 0

world.addAgent(cheese, cell=pickRandomLocation())
world.addAgent(cat)
world.addAgent(mouse)

epsilonx = (0,10000)
epsilony = (0.1,0)
epsilonm = (epsilony[1] - epsilony[0]) / (epsilonx[1] - epsilonx[0])

endAge = world.age + 10000
# endAge = world.age + 1

while world.age < endAge:
    world.update()

    '''if world.age % 100 == 0:
        mouse.ai.epsilon = (epsilony[0] if world.age < epsilonx[0] else
                            epsilony[1] if world.age > epsilonx[1] else
                            epsilonm*(world.age - epsilonx[0]) + epsilony[0])'''

    if world.age % 10000 == 0:
        print("{:d}, e: {:0.2f}, W: {:d}, L: {:d}"\
            .format(world.age, mouse.ai.epsilon, mouse.fed, mouse.eaten))
        mouse.eaten = 0
        mouse.fed = 0

world.display.activate(size=80)
world.display.delay = 1
world.drawcount = 0
c2 = 0
while 1:
    c2 = c2 + 1
    time.sleep(0.2)
    world.update(mouse.fed, mouse.eaten)
    print(len(mouse.ai.q)) # print the amount of state/action, reward 
                          # elements stored
    import sys
    bytes = sys.getsizeof(mouse.ai.q)
    print("Bytes: {:d} ({:d} KB)".format(bytes, bytes//1024))
    if QLearn.useAI:
        if c2%1000 == 0:
            c2 = 0
            pkl_filename2 = "mouse.pkl"
            with open(pkl_filename2, 'wb') as file:
                pickle.dump(mouse.ai.q, file)


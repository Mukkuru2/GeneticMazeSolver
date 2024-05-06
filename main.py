import random
import copy
import time
import os
import maze
import math
from tkinter import *   

nGenes = 500
nAgents = 100
nMutated = 5

# Modifiers - before and after finish is found
modifiers = {
    "coverage":{
        "goalDistance": [0.1, 1],
        "coverage": [1, 0],
        "geneLength": [0.01, 0.01],
    },
    
    "distance": {
        "goalDistance": [1, 1],
        "geneLength": [0.01, 0.01],
        "backtrack": [1, 0]}}

currentModifier = modifiers["distance"]
modifierset = 0

lastTopGenes = []

globalAgents = []
nIteration = 0

maze = maze.getMaze()

movements = {
    0: (0, -1),  # Up
    1: (1, 0),   # Right
    2: (0, 1),   # Down
    3: (-1, 0)}  # Left

mutationList = [
    [30, nMutated],
    [30, nMutated * 3],
    [20, nMutated * 5]
]

def getRandomGene() -> int:
    ## set two variables to a random number
    return random.randint(0, 3)

def getRandomGenome() -> list:
    genome = []
    for i in range(0, nGenes):
        genome.append(getRandomGene())
    return genome


def checkWallAhead(x, y, direction) -> bool:

    # get the movement from the direction
    movement = movements[direction]

    # get the new x and y
    x += movement[0]
    y += movement[1]

    # check if the new x and y are within the maze
    if x < 0 or x >= len(maze[0]) or y < 0 or y >= len(maze):
        return True
    # check if the new x and y are a wall
    elif maze[y][x] == 1:
        return True
    else:
        return False


def getStartPos(_maze):
    # Get the x and y of the agent which has a value of 2 in the maze array
    for y in range(0, len(_maze)):
        for x in range(0, len(_maze[y])):
            if _maze[y][x] == 2:
                return x, y
            

def getGoalPos(_maze):
    # Get the x and y of the agent which has a value of 2 in the maze array
    for y in range(0, len(_maze)):
        for x in range(0, len(_maze[y])):
            if _maze[y][x] == 3:
                return x, y

def moveInMaze(x, y, direction) -> tuple:
    if not checkWallAhead(x, y, direction):
        movement = movements[direction]
        x += movement[0]
        y += movement[1]
    return x, y

def solveMazeFromGenome(genome) -> tuple:
    xAgent, yAgent = getStartPos(maze)

    # Loop through all genes in the genome and move the agent accordingly if there is no wall ahead
    for i in range(0, len(genome)):
        xAgent, yAgent = moveInMaze(xAgent, yAgent, genome[i])

    return xAgent, yAgent
    
def heuristicCoverage(x, y, genome) -> float:
    xGoal, yGoal = getGoalPos(maze)
    # get the distance from the agent to the goal
    goalDist = math.sqrt((x - xGoal) ** 2 + (y - yGoal) ** 2)

    # Give a score to cover as much ground as possible
    coverage = 0
    visited = []
    xVisited, yVisited = getStartPos(maze)
    for i in range(0, len(genome) - 1):
        xVisited, yVisited = moveInMaze(xVisited, yVisited, genome[i])
        if (xVisited, yVisited) not in visited:
            coverage -= 1
            visited.append((xVisited, yVisited))

    # Return an addition of the distance to the goal, the length of the genome and the backtrack score.
    return goalDist * currentModifier["goalDistance"][modifierset] + \
                coverage * currentModifier["coverage"][modifierset] + \
                len(genome) * currentModifier["geneLength"][modifierset]

def heuristicDistance(x, y, genome) -> float:
    xGoal, yGoal = getGoalPos(maze)
    # get the distance from the agent to the goal
    goalDist = math.sqrt((x - xGoal) ** 2 + (y - yGoal) ** 2)

    # Decides if the modifierset should be status 0 or 1 (0 for before reaching the goal,
    # focus on expanding, 1 for after reaching the goal, focus on efficiency)
    global modifierset
    if (goalDist < 1):
        modifierset = 1

    # Motivate the agent to spread out near the front of the maze and to not directly backtrack. Gives points for spreading out at the front of the maze
    backtrack = 0
    for i in range(0, len(genome) - 1):
        if genome[i] + genome[i + 1] == 2 or genome[i] + genome[i + 1] == 4:
            backtrack += (i - len(genome)) / len(genome)

    # Return an addition of the distance to the goal, the length of the genome and the backtrack score.
    return goalDist * currentModifier["goalDistance"][modifierset] + \
                len(genome) * currentModifier["geneLength"][modifierset] + \
                backtrack * currentModifier["backtrack"][modifierset]

modifiers["coverage"]["function"] = heuristicCoverage
modifiers["distance"]["function"] = heuristicDistance

def mutate(genome, mutations) -> list:
    # Change nMutated random genes
    for i in range(0, mutations):
        # Either mutate a gene, pop a gene or append a gene
        _r = random.random()
        if _r < 0.33:
            genome[random.randint(0, len(genome) - 1)] = getRandomGene()
        elif _r < 0.67:
            genome.pop(random.randint(0, len(genome) - 1))
        else:
            genome.insert(random.randint(0, len(genome)), getRandomGene())
    
    return genome

def addMutatedAgents(agents, percentage, mutationAmount, nBestAgents) -> list:
    
    for i in range(0, (int)(nAgents * percentage / 100)):
        _agent = copy.deepcopy(agents[i % nBestAgents])
        _agent["genome"] = mutate(_agent["genome"], mutationAmount)
        agents.append(_agent)
    
    return agents

def newGeneration(agents) -> list:
    # Get the best 10% agents (plus some extra to ensure the size of the list stays the same)
    agents = agents[:int(len(agents)/10)]

    _len = len(agents)
    # Add back the agents, but add a mutation to the duplicates
    for i in range(0, len(mutationList)):
        agents = addMutatedAgents(agents, mutationList[i][0], mutationList[i][1], _len)

    # Add random agents to the list to get back to the original size
    for i in range(0, nAgents - len(agents)):
        agents.append({
            "genome": getRandomGenome(),
            "fitness": 0
        })

    return agents

    
def iteration(agents) -> list:
    _agents = []
    # Loop through all genomes
    for i in range(0, nAgents):
        genome = agents[i]["genome"]
        x, y = solveMazeFromGenome(genome)

        heuristicValue = currentModifier["function"](x, y, genome)

        _agents.append ({
            "genome": genome,
            "fitness": heuristicValue,
            "distance": abs(x - getGoalPos(maze)[0]) + abs(y - getGoalPos(maze)[1])
        })
        
    _agents.sort(key=lambda x: x["fitness"])
    return _agents

def updateCanvas(agents):
    c.delete("all")

    # Draw the maze
    for y in range(0, len(maze)):
        for x in range(0, len(maze[y])):
            if maze[y][x] == 1:
                c.create_rectangle(x * 10, y * 10, x * 10 + 10, y * 10 + 10, fill="black")
            elif maze[y][x] == 2:
                c.create_rectangle(x * 10, y * 10, x * 10 + 10, y * 10 + 10, fill="green")
            elif maze[y][x] == 3:
                c.create_rectangle(x * 10, y * 10, x * 10 + 10, y * 10 + 10, fill="red")

    # Draw the best agent
    xAgent, yAgent = getStartPos(maze)

    for i in range(0, len(agents[0]["genome"])):
        if not checkWallAhead(xAgent, yAgent, agents[0]["genome"][i]):
            movement = movements[agents[0]["genome"][i]]
            xAgent += movement[0]
            yAgent += movement[1]
            c.create_rectangle(xAgent * 10, yAgent * 10, xAgent * 10 + 10, yAgent * 10 + 10, fill="blue")


    c.pack()

def iterationLoop():
    global globalAgents
    global nIteration
    agents = iteration(globalAgents)

    # Update the canvas
    updateCanvas(globalAgents)


    # Clear the console
    os.system('cls')

    print("Iteration: " + str(nIteration))
    print("Distance: " + str(agents[0]["distance"]))
    print("Gene Length: " + str(len(agents[0]["genome"])))
    print("Fitness: " + str(agents[0]["fitness"]))
    if agents[0]["distance"] == 0:
        print("Solution found!")
        print("Genome: " + str(agents[0]["genome"]))
        

    # Get a new generation
    agents = newGeneration(agents)
    nIteration += 1
    top.after(100, iterationLoop)
    globalAgents = agents


def start():
    # Assign all agents a random genome
    for i in range(0, nAgents):
        genome = getRandomGenome()
        globalAgents.append ({
            "genome": genome,
            "fitness": 0
        })

start()

top = Tk()
top.geometry("1000x1000")  
    
#creating a simple canvas  
c = Canvas(top,bg = "pink",height = 1000,width = 1000)

top.after(10, iterationLoop)
top.mainloop()
# Assignment 4 - generation and AI

# Genetic algorithm to solve a maze

In this assignment I genetically teach some creatures (referred to as agents) how to solve mazes. For this the creatures have a genome with instructions on how they approach a specific maze. This is randomly generated and randomly mutated. A “fitness” or heuristic score decides how good a genome is, and if it gets to continue existing.

## The basic idea

I decided to work from the bottom up in this assignment. I roughly sketched out the different functions:

```python
getRandomGene() -> int # Get a single gene
getRandomGenome() -> list # Get a full genome of a certain length
solveMazeFromGenome(genome) -> tuple # Apply one genome on the maze. Return the final x and y
heuristic(x, y, genome) -> int # Give a score to the genome depending on the result
newGeneration(agents) -> list # Create a new generation of agents
mutate(genome) -> list # Apply several mutations to a genome
```

I started from top to bottom and looked at what I needed.

## Coding these functions

I decided to use python for this project due to its simplicity and easy and fast modification ability.

### The genome

First the function to create a random gene which decides a direction. This is just a random number from 0 to 3.

```python
def getRandomGene() -> int:
    ## set two variables to a random number
    return str(random.randint(0, 3))
```

A genome is built up by adding a gene to a list `nGenes` times.

```python
def getRandomGenome() -> list:
    genome = []
    for i in range(0, nGenes):
        genome.append(getRandomGene())
    return genome
```

### Solving a maze

A maze is made as a 2D list from 0s and 1s. A 2 is in the start position, and a 3 is the goal position. For the first try this example was used, however as seen in later chapters more complex examples have been tested.

```python
maze = [
[0, 0, 1, 0, 0, 0],
[2, 0, 1, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 3, 0]]
```

The randomly generated genome is applied on a maze.

```python
def solveMazeFromGenome(genome) -> list:
    xAgent, yAgent = getStartPos(maze)

    # Loop through all genes in the genome and move the agent accordingly if there is no wall ahead
    for i in range(0, len(genome)):
        xAgent, yAgent = moveInMaze(xAgent, yAgent, genome[i])

    return xAgent, yAgent
```

The  movement through the maze is handled by its own function. This applies a direction to an x and a y, and returns the new x and y.

```python
movements = {
    0: (0, -1),  # Up
    1: (1, 0),   # Right
    2: (0, 1),   # Down
    3: (-1, 0)}  # Left

### [some other functions in between] ###

def moveInMaze(x, y, direction) -> tuple:
    if not checkWallAhead(x, y, direction):
        movement = movements[direction]
        x += movement[0]
        y += movement[1]
    return x, y
```

Handling the cases for walls was more complex than I initially thought. Since we’re working with arrays, negative indices or indices larger than the list are forbidden. Those are seen as a wall and are therefore not actually counted as a movable space.

```python
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
```

### Rating the genome

A heuristic function gives a score to the result. The heuristic function is one of the most important functions in the whole script. This function rates how good a genome is and decides what the agent “wants” to pursue. For now this is just the distance to the goal.

```python
def heuristic(x, y, agent) -> float:
    xGoal, yGoal = getGoalPos(maze)
    # get the distance from the agent to the goal
    goalDist = math.sqrt((x - xGoal) ** 2 + (y - yGoal) ** 2)

    return goalDist 
```

### Creating a population

A first generation is created randomly.

```python
def start():
    # Assign all agents a random genome
    for i in range(0, nAgents):
        genome = getRandomGenome()
        globalAgents.append ({
            "genome": genome,
            "fitness": 0
        })
```

### Modifying and mutating the population

The next code block is quite long. It returns a new generation based on a pre-configured list of how many mutations a part of the agents set should get. The specific mutations will be talked about one block below. The best 10% of the agents is separated, and those get copied. Mutations are applied to the copies. The originals remain.

```python
# Defines what percentage of agents should get how many mutations.
mutationList = [
    [30, nMutated],
    [30, nMutated * 3],
    [20, nMutated * 5]
]

### [A lot of stuff in between] ###

def addMutatedAgents(agents, percentage, mutationAmount, nBestAgents) -> list:
    
    for i in range(0, (int)(nAgents * percentage / 100)):
        _agent = copy.deepcopy(agents[i % nBestAgents])
        _agent["genome"] = mutate(_agent["genome"], mutationAmount)
        agents.append(_agent)
    
    return agents

def newGeneration(agents) -> list:
    # Get the best 10% agents
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
```

There are three possible mutations: changing a gene, adding a gene or removing a gene.

<aside>
<img src="https://www.notion.so/icons/dna_gray.svg" alt="https://www.notion.so/icons/dna_gray.svg" width="40px" /> The added gene is not added in a random place! It’s always added at the front of the gene. This gives the genome a huge advantage, since usually the front of the genome is where the most action happens. You can see that this is one of the most common mutations due to the genome length growing quickly while trying to solve the maze.

This is changed at a later stage, see chapter “Improvements”

</aside>

```python
def mutate(genome, mutations) -> list:
    # Genes that are still not consistent with the optimal genes have a higher chance of being mutated
    startMutationGene = (int)(random.random() * optimalGenes)

    # Change nMutated random genes
    for i in range(0, mutations):
        # Either mutate a gene, pop a gene or append a gene
        _r = random.random()
        if _r < 0.33:
            genome[random.randint(0, len(genome) - 1)] = getRandomGene()
        elif _r < 0.67:
            genome.pop(random.randint(0, len(genome) - 1))
        else:
            genome.append(getRandomGene())
    
    return genome
```

### Creating the iterative loop

To tie this all together an iterative loop is ran. Very similar to many game engines there exist a start function and a loop function.

```python
def iterationLoop():
    global globalAgents
    global nIteration
    agents = iteration(globalAgents)

    # Clear the console
    os.system('cls')

    print("Iteration: " + str(nIteration))
    print("Distance: " + str(agents[0]["distance"]))
    print("Gene Length: " + str(len(agents[0]["genome"])))
    if agents[0]["distance"] == 0:
        print("Solution found!")
        print("Genome: " + str(agents[0]["genome"]))
        

    # Get a new generation
    agents = newGeneration(agents)
    nIteration += 1
    globalAgents = agents

start()

# Do the iteration loop n times
for i in range(0, nIteration):
		iterationLoop()
```

The `iteration()` function itself does most of the hard work of applying all agents’ genome, applying the heuristic and calculating the distance.

```python
def iteration(agents) -> list:
    _agents = []
    # Loop through all genomes
    for i in range(0, nAgents):
        genome = agents[i]["genome"]
        x, y = solveMazeFromGenome(genome)
        _agents.append ({
            "genome": genome,
            "fitness": heuristic(x, y, agents[i]["genome"]),
            "distance": abs(x - getGoalPos(maze)[0]) + abs(y - getGoalPos(maze)[1])
        })
        
    _agents.sort(key=lambda x: x["fitness"])
    return _agents
```

## Improvements

I experimented quite a bit with the heuristic. This is one of the most important functions in determining the success of the algorithm. With just the distance heuristic the algorithm was extremely prone to getting stuck in local maxima. This meant that fairly open areas that mostly had routes around objects were fine, but mazes where the agent had to backtrack bigger distances were not. There were several ways I tried to improve the performance.

### Spreading out

The first and biggest improvement was a reward for spreading out near the “tip” of the agent, the place where the last gene was activated. Due to the fact that it added genes in the front, this caused a behaviour that “explored” the nearby area. This mostly improved the status in the more open areas, however it also improved the maze capabilities - as long as the maze didn’t involve backtracking too much.

### Gene length

Another improvement was to add a different behaviour if the agent reached the goal, this was mostly one I myself wanted to add. This new behaviour would try to reduce the length of the genome.

### Maximise coverage

Another improvement I tried was to reward the agents for maximising their coverage on the board in hopes of solving a more complex maze. This however didn’t work - at all. See the results chapter.

### Final heuristic

In total I tried a lot of different combinations of weights for heuristics. I found that for the distance based heuristic, the following modifiers and code worked best.

```python
modifiers = {
        "goalDistance": [1, 1],
        "geneLength": [0.01, 0.01],
        "backtrack": [1, 0]}

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
    return goalDist * modifiers["goalDistance"][modifierset] + \
                len(genome) * modifiers["geneLength"][modifierset] + \
                backtrack * modifiers["backtrack"][modifierset]
```

## Results

![True maze: 200 iterations (800 genes)](Assignment%204%20-%20generation%20and%20AI%206fabda3d9afc4cbc8db5c2088d1d7c85/Untitled.png)

True maze: 200 iterations (800 genes)

![True maze: 1000 iterations (2000 genes)](Assignment%204%20-%20generation%20and%20AI%206fabda3d9afc4cbc8db5c2088d1d7c85/Untitled%201.png)

True maze: 1000 iterations (2000 genes)

![50 iterations](Assignment%204%20-%20generation%20and%20AI%206fabda3d9afc4cbc8db5c2088d1d7c85/Untitled%202.png)

50 iterations

![200 iterations](Assignment%204%20-%20generation%20and%20AI%206fabda3d9afc4cbc8db5c2088d1d7c85/Untitled%203.png)

200 iterations

![300 iterations: 950 genes](Assignment%204%20-%20generation%20and%20AI%206fabda3d9afc4cbc8db5c2088d1d7c85/Untitled%204.png)

300 iterations: 950 genes

![2000 iterations: 250 genes](Assignment%204%20-%20generation%20and%20AI%206fabda3d9afc4cbc8db5c2088d1d7c85/Untitled%205.png)

2000 iterations: 250 genes

![Coverage heuristic - 300 iterations](Assignment%204%20-%20generation%20and%20AI%206fabda3d9afc4cbc8db5c2088d1d7c85/Untitled%206.png)

Coverage heuristic - 300 iterations

![Coverage heuristic - 2000 iterations](Assignment%204%20-%20generation%20and%20AI%206fabda3d9afc4cbc8db5c2088d1d7c85/Untitled%207.png)

Coverage heuristic - 2000 iterations
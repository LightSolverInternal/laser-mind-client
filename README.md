
## LaserMind Client
The LaserMind Client is a Python package designed to interface with the LaserMind Cloud to facilitate solving Quadratic Unconstrained Binary Optimization (QUBO) problems.

This package is designated for internal access to features during development process as well as to serve as a prototype for future versions of the production LaserMind Client.

## Features
- QUBO Problem Solving: The solve_qubo function accepts a QUBO problem, represented either as a 2D array (matrix) or an adjacency list, and returns the solution.
- Synchronous and Asynchronous Operation: Users can choose between blocking (synchronous) and non-blocking (asynchronous) modes for QUBO problem solving.
- Flexible Installation: Compatible with both Windows and Ubuntu systems.


### Solve QUBO
The solve_qubo function handles the computation of QUBO problems, either represented by a 2d array (matrix) or by an adjacency list. For code samples, see the "Usage" chapter.

#### Input Matrix Validity
- The matrix must be square.
- The matrix supports int or float cell values.

#### Return Value
A dictionary with the following fields:
```
- 'id' - Unique identifier of the solution.
- 'solution' - The solution as a Python list() of 1s and 0s.
- 'objval' - The objective value of the solution.
- 'solverRunningTime' - Time spent by the solver to calculate the problem.
- 'receivedTime' - Timestamp when the request was received by the server.
```

### Synchronous and Asynchronous Usage
- Synchronous Mode (Default): The waitForSolution flag is set to True by default. The function blocks until a result is received.
- Asynchronous Mode: Set waitForSolution to False. The function returns immediately with a token object, allowing the script to continue while the server processes the QUBO problem.

## Prerequisites
- Valid credetials for connecting to the LaserMind cloud.
- This repository cloned to your work environment.
- Python 3.10.
- Operating System: Linux or Windows. Tested on Ubuntu 20.04 and Windows 11.
- Highly Recommended: use a virtual environment before installing laser-mind-client.

## Authentication
Initialization of the `LaserMind` class automatically forms a secure and authenticated connection with the LaserMind Cloud.

Subsequent calls by the same user are similarly secure and authenticated.

## Usage
To begin solving any QUBO problem, first create an instance of the ```LaserMind``` class. This class represents the client that requests solutions from the LaserMind Cloud. To solve a problem, call the ```solve_qubo``` function.

### Solve QUBO Matrix
In this basic example, we create a matrix representing a QUBO problem and solve it using the LaserMind client.
We use the solve_qubo function that receives a 2d array representing a QUBO problem - ```matrixData``` and
the desired calculation time in seconds - ```timeout```.

```python
import numpy
from laser_mind_client import LaserMind

# Create a mock QUBO problem
quboProblemData = numpy.random.randint(-1, 2, (10,10))

# symmetrize our matrix
quboProblemData = (quboProblemData + quboProblemData.T) // 2

# Connect to the LaserMind cloud
lsClient = LaserMind()

res = lsClient.solve_qubo(matrixData = quboProblemData, timeout=1)

print(res)
```


### Solve QUBO Adjacency List
In this example, we describe our QUBO problem using an adjacency list, which is useful for sparse matrices. We send this adjacency list as a 2d arrray into the ```edgeList``` parameter.

Note: users may either provide a value to ```matrixData``` or to ```edgeList```, but not to both.

```python
from laser_mind_client import LaserMind

# Create a mock QUBO problem
quboListData = [
    [1,1,5],
    [1,2,-6],
    [2,2,3],
    [2,3,-1],
    [3,10,1]]


# Connect to the LaserMind cloud
lsClient = LaserMind()

res = lsClient.solve_qubo(edgeList=quboListData, timeout=1)

print(res)
```


### Solve QUBO Matrix Using Asynchronous Flow
In this example, we demonstrate how to solve a QUBO problem asynchronously using the LaserMind client. We begin by creating a matrix to represent our QUBO problem. The `solve_qubo` function is then utilized with the following parameters:
   - `matrixData`: A 2D array representing the QUBO problem.
   - `timeout`: The desired time limit for the calculation in seconds.
   - `waitForSolution`: A boolean flag set to `False` to indicate non-blocking mode.

```python
import numpy
from laser_mind_client import LaserMind

# Create a mock QUBO problem
quboProblemData = numpy.random.randint(-1, 2, (10,10))

# symmetrize our matrix
quboProblemData = (quboProblemData + quboProblemData.T) // 2

# Connect to the LaserMind cloud
lsClient = LaserMind()

# Request a solution to our QUBO problem and get the request token for future retrieval.
# This call does not block until the problem is solved.
requestToken = lsClient.solve_qubo(matrixData = quboProblemData, timeout=1, waitForSolution=False)

# Here we can run code not dependant on our request while the server processes.

# Retrieve the solution using the get_solution_sync method.
# This blocks until the solution is acquired.
res = lsClient.get_solution_sync(requestToken)

print(res)
```

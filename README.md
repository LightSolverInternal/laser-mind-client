
# LaserMind
Internal client API package for accessing the SaaS provided by [LightSolver](https://Lightsolver.com).

This package is designated for internal access to features during development process
as well as to serve as a prototype for future versions of the production LaserMind client.

The automatic tests for this package can serve as a sanity integration test.

## The LaserMind client

LaserMind is a python package that is a one-stop-shop for using LightSolver's services.

On initialization of the `LaserMind` class, a secured and authenticated connection
with the LightSolver cloud is formed.
Subsequent calls by the same user are authenticated and secured.

### Solve QUBO

Currently, our main efforts are to develop QUBO solving algorithms.
For this we have created a flow where each problem sent is solved by a
parallel hyper-heuristic.
The `solve_qubo` function receives a QUBO problem described by either a 2d array (matrix)
or an adjecency list and returns the calculated result.

### Flow of operation

LaserMind API calls can be used in both synchronous and asynchronous code sequences.
This is achieved by a dual strategy for the LaserMind functions, given by the `waitForSolution` flag.

By default (synchronous), the `waitForSolution` flag is set to `True`.
in this case when calling LaserMind functions the function will block until
a result is returned from the LightSolver cloud and then return the calculated result.

We can also take an asynchronous approach in which we do not wait for the QUBO
calculation to be done before executing more code.
In this case, we set the `waitForSolution` to `False` when calling a function.
When this flag is off, the function will not wait for the computation to complete
and instead return immediatly with a token object, that can be used to retrieve
the solution in a later time.
This allows our script to perform additional operations while the LightSolver cloud
is busy with solving our QUBO problem.

## Setting up
Getting started is quite starightforward and requires a few one-time steps.

### Prerequisites
- Have valid credetials for connecting to the LaserMind cloud.
- Install our PIP Package


### Installation

TBD

It is strongly recommended to use virtual environments when using this package.

## Basic Usage
LasrMind usage is prettry simple and fun, here are a few examples

### Simple QUBO matrix
In this basic example, we create a small matrix representing a QUBO problem
and solve it using the LaserMind client.
We will user the solve_qubo function that receives
a 2d array representing a QUBO problem - ```matrixData``` and
the overall desired calculation time - ```timeout```.

The retrned value is a dictionary containing the calculated result along with other information.

```python
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

### Describing a sparse QUBO problem using an adjecency list

We can also use an adjecency list (sparse matrix representation) as an input
to solve_qubo instead of a 2d arrray by using the ```edgeList``` parameter.

note that when you use a list you cannot use set the ```matrixData``` parameter.

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

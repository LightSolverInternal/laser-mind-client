
## LightSolver Platform Client
The LightSolver Platform Client is a Python package designed to interface with the LightSolver Cloud to facilitate solving Quadratic Unconstrained Binary Optimization (QUBO) problems.

This package is designated for internal access to features during the development process, as well as serves as a prototype for future versions of the production LightSolver Platform Client.

## Features
- **QUBO Problem Solving:** The `solve_qubo` function accepts a QUBO problem, represented either as a 2D array (matrix) or an adjacency list, and returns the solution.
- **Synchronous and Asynchronous Operation:** Users can choose between blocking (synchronous) and non-blocking (asynchronous) modes for QUBO problem solving.
- **Flexible Installation:** Compatible with both Windows and MacOS systems.

### Solve QUBO
The `solve_qubo` function handles the computation of QUBO problems, either represented by a 2D array (matrix) or by an adjacency list. For code samples, see the **Usage** section.

#### Input Matrix Validity
- The matrix must be square.
- The matrix supports int or float cell values.

#### Return Value
A dictionary with the following fields:
```
- 'id': Unique identifier of the solution.
- 'solution': The solution as a Python list() of 1s and 0s.
- 'objval: The objective value of the solution.
- 'solverRunningTime': Time spent by the solver to calculate the problem.
- 'receivedTime': Timestamp when the request was received by the server.
```

### Synchronous and Asynchronous Usage
- **Synchronous Mode (Default):** The `waitForSolution` flag is set to **True** by default. The function blocks operations until a result is received.
- **Asynchronous Mode:** Set `waitForSolution` to **False**. The function returns immediately with a token object, allowing the script to continue while the server processes the QUBO problem.

## Setting Up

### Prerequisites
- Operating System: MacOS or Windows 11.
- Valid token for connecting to the LightSolver Cloud (provided separately).
- Python 3.10 or higher ([Download Here](https://www.python.org/downloads/release/python-31011/)).
    - Select the appropriate MacOS/Windows version at the bottom.
    - Note: for Windows installation, switch on the "Add to Path" option in the wizard.
- Highly Recommended: Use a virtual environment before installing laser-mind-client (Please see detailed action further below under the relevant OS).

### Installation
Complete the installation on Windows or MacOS as described below.
For further assistance with setup or connection issues, contact support@lightsolver.com.

#### Windows
1. Press the windows key, type "cmd", and select "Command Prompt".

2. Navigate to the root folder of the project where you plan to use the LightSolver Client:
```sh
    cd <your project folder>
```

3. (Recommended) Create and activate the virtual environment:
```sh
    python -m venv .venv
    .venv\Scripts\activate
```

4. Install the laser-mind-client package:
```sh
    pip install laser-mind-client
```

5. (Recommended) Test using one of the provided test examples. Under the above project folder unzip "lightsolver_onboarding.zip."
```sh
    cd lightsolver_onboarding
    open test_solve_qubo_matrix.py file for edit
    enter the provided TOKEN in line 6 (userToken = "<my_token>")
    python ./tests/test_solve_qubo_matrix.py
```


#### MacOS
1. Open new terminal window.

2. Navigate to the root folder of the project where you plan to use the LightSolver Client:
```sh
    cd <your project folder>
```

3. (Recommended) Create and activate the virtual environment:
```sh
    python3 -m venv .venv
    chmod 755  .venv/bin/activate
    source .venv/bin/activate
```

4. Install the laser-mind-client package.
```sh
    pip install laser-mind-client
```

8. (Recommended) Test using one of the provided test examples. Under the above project folder unzip "lightsolver_onboarding.zip."
```sh
    cd lightsolver_onboarding
    open test_solve_qubo_matrix.py file for edit
    enter the provided TOKEN in line 6 (userToken = "<my_token>")
    python3 ./tests/test_solve_qubo_matrix.py
```

***
## Authentication
Initialization of the `LaserMind` class automatically forms a secure and authenticated connection with the LightSolver Cloud.
Subsequent calls by the same user are similarly secure and authenticated.

## Usage
To begin solving any QUBO problem:
1. Create an instance of the ```LaserMind``` class. This class represents the client that requests solutions from the LightSolver Cloud.
2. Call the ```solve_qubo``` function using either a matrix or an adjacency list.
**Note:** You may either provide a value for ```matrixData``` or for ```edgeList```, but not both.

### Solve QUBO Matrix Example
This example creates a matrix representing a QUBO problem and solves it using the LightSolver Platform Client.
The `solve_qubo` function is used with the following parameters:
- ```matrixData```: A 2D array representing the QUBO problem.
- ```timeout```: The required time limit for the calculation in seconds.

```python
import numpy
from laser_mind_client_meta import MessageKeys
from laser_mind_client import LaserMind

# Enter your TOKEN here
userToken = "<my_token>"

# Create a mock QUBO problem
quboProblemData = numpy.random.randint(-1, 2, (10,10))

# Symmetrize the matrix
quboProblemData = (quboProblemData + quboProblemData.T) // 2

# Connect to the LightSolver Cloud
lsClient = LaserMind(userToken=userToken)

res = lsClient.solve_qubo(matrixData = quboProblemData, timeout=1)

assert MessageKeys.SOLUTION in res, "Test FAILED, response is not in expected format"

print(f"Test PASSED, response is: \n{res}")
```

### Solve QUBO Adjacency List Example
This example describes a QUBO problem using an adjacency list. This is useful for sparse matrices.
The `solve_qubo` function is used with the following parameters:
- ```edgeList```: The adjacency list representing the QUBO problem.
- ```timeout```: The required time limit for the calculation in seconds.


```python
from laser_mind_client_meta import MessageKeys
from laser_mind_client import LaserMind

# Enter your TOKEN here
userToken = "<my_token>"

# Create a mock QUBO problem
quboListData = [
    [1,1,5],
    [1,2,-6],
    [2,2,3],
    [2,3,-1],
    [3,10,1]]

# Connect to the LightSolver Cloud
lsClient = LaserMind(userToken=userToken)

res = lsClient.solve_qubo(edgeList=quboListData, timeout=1)

assert MessageKeys.SOLUTION in res, "Test FAILED, response is not in expected format"

print(f"Test PASSED, response is: \n{res}")
```

### Solve QUBO Matrix using Asynchronous Flow
This example demonstrates how to solve a QUBO problem asynchronously using the LightSolver Platform Client.
Begin by creating a matrix to represent your QUBO problem.
The `solve_qubo` function is used with the following parameters:
   - `matrixData`: A 2D array representing the QUBO problem.
   - `timeout`: The desired time limit for the calculation in seconds.
   - `waitForSolution`: A boolean flag set to `False` to indicate non-blocking mode.

```python
import numpy
from laser_mind_client_meta import MessageKeys
from laser_mind_client import LaserMind

# Enter your TOKEN here
userToken = "<my_token>"

# Create a mock QUBO problem
quboProblemData = numpy.random.randint(-1, 2, (10,10))

# Symmetrize our matrix
quboProblemData = (quboProblemData + quboProblemData.T) // 2

# Connect to the LightSolver Cloud
lsClient = LaserMind(userToken=userToken)

# Request a solution to the QUBO problem and get the request token for future retrieval.
# This call does not block operations until the problem is solved.
requestToken = lsClient.solve_qubo(matrixData = quboProblemData, timeout=1, waitForSolution=False)

# You can run other code here that is not dependant on the request, while the server processes your request.

# Retrieve the solution using the get_solution_sync method.
# This blocks operations until the solution is acquired.
res = lsClient.get_solution_sync(requestToken)

assert MessageKeys.SOLUTION in res, "Test FAILED, response is not in expected format"

print(f"Test PASSED, response is: \n{res}")
```


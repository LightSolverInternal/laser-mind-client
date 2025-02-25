
## LightSolver Client
The LightSolver Client is a Python package designed to interface with the LightSolver Cloud Platform to facilitate solving problems on LightSolver's LPU (Laser Processing Unit) and dLPU (digital-LPU) solvers.

This package is designated for early access to features during the development process and serves as a prototype for future versions of the production LightSolver Client.

## Features
- **QUBO Problem Solving:** The `solve_qubo` function accepts a QUBO problem, represented either as a 2D array (matrix) or an adjacency list, and returns the solution using the dLPU.
- **Synchronous and Asynchronous Operation:** Users can choose between blocking (synchronous) and non-blocking (asynchronous) modes during problem solving.
- **Fetching Account Details:** Account information is available through this client. Includes: email, dLPU solve time remaining, dLPU variable count ("spin") limit and the user's expiration date.
- **Flexible Installation:** Compatible with both Windows and MacOS systems.

### Solve QUBO
The `solve_qubo` function solves QUBO problems, either represented by a 2D array (matrix) or by an adjacency list, over the dLPU. For code samples, see the /tests directory.

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

### Fetching Account Details
The `get_account_details()` function returns a python dictionary containing the following keys:
```
- 'dlpu_spin_limit': an int indicating the largest matrix size the user can send to the dlpu (dimensions of dlpu_spin_limit X dlpu_spin_limit).
- 'username': the username / email associated with this user. String.
- 'expiration_date: an Epoch timestamp indicating when the user expires. Int.
- 'dlpu_credit_seconds': solve time remaining for the user. Float.
```

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
2. By default, all logs are printed to laser-mind.log file in current directory and to console. Output to console can be disabled by setting ```logToConsole=False```
3. Call the ```solve_qubo``` function using either a matrix or an adjacency list.
**Note:** You may either provide a value for ```matrixData``` or for ```edgeList```, but not both.

## Examples
Find examples of every feature in laser-mind-client under the "tests/" directory.

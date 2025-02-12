####################################################################################################
# This example creates a QUBO matrix and solves it using the LPU over LightSolver's platform.
# The `solve_qubo` function is used with the following parameters:
# - `matrix_data`: A 2D array representing the QUBO problem.
# - `timeout`: The required time limit for the calculation in seconds.
####################################################################################################

import numpy
from laser_mind_client_meta import MessageKeys
from laser_mind_client import LaserMind

# Enter your TOKEN here
user_token = "<TOKEN>"

# Create a mock QUBO problem
quboProblemData = numpy.random.randint(-1, 2, (10,10))

# Symmetrize our matrix
quboProblemData = (quboProblemData + quboProblemData.T) // 2

# Connect to the LightSolver Cloud
lsClient = LaserMind(user_token=user_token)

# Request a LPU solution to the QUBO problem
res = lsClient.solve_qubo_lpu(matrix_data = quboProblemData)

assert 'data' in res
assert MessageKeys.SOLUTION in res['data'], "Test FAILED, response is not in expected format"

print(f"Test PASSED, response is: \n{res}")
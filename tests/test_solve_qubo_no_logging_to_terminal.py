####################################################################################################
# This example solves a QUBO matrix using the dLPU over LightSolver's platform while avoiding
# logging to the terminal.
####################################################################################################
import numpy
from laser_mind_client_meta import MessageKeys
from laser_mind_client import LaserMind

# Enter your TOKEN here
user_token = "<TOKEN>"

# Create a mock QUBO problem
quboProblemData = numpy.random.randint(-1, 2, (10,10))

# Symmetrize the matrix
quboProblemData = (quboProblemData + quboProblemData.T) // 2

# Connect to the LightSolver Cloud, Do NOT log to terminal (will still log to file)
lsClient = LaserMind(user_token=user_token, log_to_console=False)

res = lsClient.solve_qubo(matrix_data = quboProblemData, timeout=1)

assert MessageKeys.SOLUTION in res, "Test FAILED, response is not in expected format"

print(f"Test PASSED, response is: \n{res}")
####################################################################################################
# This example solves a QUBO matrix using the dLPU over LightSolver's platform while avoiding
# logging to the terminal.
####################################################################################################
import numpy
from laser_mind_client_meta import MessageKeys
from laser_mind_client import LaserMind

# Enter your TOKEN here
userToken = "f4ALtwB+zTt1lXJKZdtpIP9lliJUY8I9Oj7W+plCWw6NS3t4nT2aQcF/7scNWCbwNm79sY+acj5SbuToC4bTunyGtmGtDn2qkse1fzz0Y/9LDqxL/P4U/CtkD0qeFDGI"

# Create a mock QUBO problem
quboProblemData = numpy.random.randint(-1, 2, (10,10))

# Symmetrize the matrix
quboProblemData = (quboProblemData + quboProblemData.T) // 2

# Connect to the LightSolver Cloud, Do NOT log to terminal (will still log to file)
lsClient = LaserMind(userToken=userToken, logToConsole=False)

res = lsClient.solve_qubo(matrixData = quboProblemData, timeout=1)

assert MessageKeys.SOLUTION in res, "Test FAILED, response is not in expected format"

print(f"Test PASSED, response is: \n{res}")
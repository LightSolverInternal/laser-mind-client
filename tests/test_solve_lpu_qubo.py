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

# Request a LPU solution to the QUBO problem
res = lsClient.solve_qubo_lpu(matrixData = quboProblemData)

assert 'data' in res
assert MessageKeys.SOLUTION in res['data'], "Test FAILED, response is not in expected format"

print(f"Test PASSED, response is: \n{res}")
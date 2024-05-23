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
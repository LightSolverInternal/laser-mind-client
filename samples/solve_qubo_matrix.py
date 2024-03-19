import numpy
from laser_mind_client import LaserMind

# Create a mock QUBO problem
quboProblemData = numpy.random.randint(-1, 2, (10,10))

# Symmetrize the matrix
quboProblemData = (quboProblemData + quboProblemData.T) // 2

# Connect to the LightSolver Cloud
lsClient = LaserMind()

res = lsClient.solve_qubo(matrixData = quboProblemData, timeout=1)

print(res)
import numpy
from laser_mind_client_meta import MessageKeys
from laser_mind_client import LaserMind

size = 25
coupMat = 0.5 * numpy.eye( size ,dtype=numpy.complex64)
coupling = (1-0.5)/(2)
for i in range(size - 1):
    coupMat[i,i+1] = coupling
    coupMat[i+1,i] = coupling

userToken = "<my_token>"

# Connect to the LightSolver Cloud
lsClient = LaserMind(userToken=userToken)

# Request a LPU solution to the CoupMat problem
res = lsClient.solve_coupling_matrix_lpu(matrixData = coupMat)

assert 'data' in res
assert  'phase_difference' in res['data']
assert  'energy_problem'   in res['data']
assert  'contrast_problem' in res['data']
assert  'solverRunningTime' in res['data']

print(f"Test PASSED, response is: \n{res}")
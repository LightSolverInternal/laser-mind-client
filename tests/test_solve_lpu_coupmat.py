####################################################################################################
# This example creates a Coupling matrix problem and solves it using the LPU over LightSolver's Platform.
# The `solve_coupling_matrix_lpu` function is used with the following parameters:
# - ```matrix_data```: A 2D array representing the coup_matrix problem.
# - ```num_runs ```: The required number or calculation runs, default 1.
####################################################################################################

import numpy
from laser_mind_client import LaserMind

user_token = "<TOKEN>"

# Generate a coupling matrix
size = 15
coup_matrix = 0.5 * numpy.eye( size ,dtype=numpy.complex64)
coupling = (1-0.5)/(2)
for i in range(size - 1):
    coup_matrix[i,i+1] = coupling
    coup_matrix[i+1,i] = coupling

# Connect to the LightSolver Cloud
lsClient = LaserMind(user_token=user_token)

# Request a LPU solution to the coup_matrix problem
res = lsClient.solve_coupling_matrix_lpu(matrix_data = coup_matrix)

assert 'data' in res
assert  'phase_difference' in res['data']
assert  'energy_problem'   in res['data']
assert  'contrast_problem' in res['data']
assert  'solverRunningTime' in res['data']

print(f"Test PASSED, response is: \n{res}")
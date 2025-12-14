####################################################################################################
# This example creates a Coupling matrix problem and scans its phase parameters on the LPU over LightSolver's Platform.
# The `solve_scan_lpu` function is used with the following parameters:
# - ```matrixData```: A 2D array representing the coupmat problem.
# - ```scanDictionary```: A dictionary containing the scan parameters.
####################################################################################################

import numpy
import os
from laser_mind_client import LaserMind

pathToTokenFile = os.path.join(os.path.dirname(__file__), "lightsolver-token.txt")

# Generate a coupling matrix
size = 15
coupling_matrix = 0.5 * numpy.eye(size, dtype=numpy.complex64)
coupling = (1-0.5)/2
for i in range(size - 1):
    coupling_matrix[i,i+1] = coupling
    coupling_matrix[i+1,i] = coupling

# number of steps in the scan
num_steps = 10
# lasers to scan
lasers_to_scan = numpy.array([[3,3]])
# phases to scan for each pair of indicies for the num_steps
phases_to_scan = numpy.zeros((lasers_to_scan.shape[0],num_steps),numpy.float32)
phases_to_scan[:] = numpy.round(numpy.linspace(0, 255, num_steps, endpoint=False)).astype(numpy.uint8) * (2 * numpy.pi / 255)
scan_dictionary = {
    "num_of_steps": num_steps,
    "lasers_to_scan": lasers_to_scan,
    "phases_to_scan": phases_to_scan
}

# Connect to the LightSolver Cloud
lsClient = LaserMind(pathToRefreshTokenFile=pathToTokenFile)

# Scan the phase parameters on the LPU
res = lsClient.solve_scan_lpu(matrixData = coupling_matrix, scanDictionary = scan_dictionary)

# Verify response format
assert 'command' in res, "Missing 'command' field"
assert 'data' in res, "Missing 'data' field"
assert 'solutions' in res['data'], "Missing 'solutions' field"

print(f"Test PASSED, response is: \n{res}")

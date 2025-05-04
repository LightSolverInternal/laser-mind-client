import numpy
from laser_mind_client_meta import MessageKeys
from laser_mind_client import LaserMind

size = 10
coup_mat = 0.5 * numpy.eye( size ,dtype=numpy.complex64)
coupling = (1-0.5)/(2)
for i in range(size - 1):
    coup_mat[i,i+1] = coupling
    coup_mat[i+1,i] = coupling


# Create a mock QUBO problem
quboProblemData = numpy.random.randint(-1, 2, (10,10))
# Symmetrize our matrix
quboProblemData = (quboProblemData + quboProblemData.T) // 2

#user_token = "<my_token>"
import os
os.environ["LS_API_RUN_URL"] = "http://dev.internal.lightsolver.com/api/v1/commands/run"
os.environ["LS_API_RUN_SECURED_URL"] = "https://devfront.internal.lightsolver.com/api/v1/commands/run"
os.environ["LS_AUTH_URL"] = "https://auth.devfront.lightsolver.com/authorize-solver-usage"
os.environ["LS_REQUEST_URL"] = "https://devfront.internal.lightsolver.com/api/v2/getsolution"
os.environ["LS_API_GET_PRESIGNED_URL"] = "https://devfront.internal.lightsolver.com/api/v1/getposturl"

user_token = "f4ALtwB+zTt1lXJKZdtpIP9lliJUY8I9Oj7W+plCWw6NS3t4nT2aQcF/7scNWCbwNm79sY+acj5SbuToC4bTunyGtmGtDn2qkse1fzz0Y/9LDqxL/P4U/CtkD0qeFDGI"

# Connect to the LightSolver Cloud
lsClient = LaserMind(userToken=user_token, logToConsole = False)

#### res = lsClient.solve_qubo(matrix_data = quboProblemData, timeout=30)

#### exit()

# Request a LPU solution to the coup_matrix problem
# res = lsClient.solve_coupling_matrix_lpu(matrixData = coup_mat)

#assert 'data' in res
#assert  'phase_difference' in res['data']
#assert  'energy_problem'   in res['data']
#assert  'contrast_problem' in res['data']
#assert  'solverRunningTime' in res['data']

#print(f"Test PASSED, response is: \n{res}")




# Connect to the LightSolver Cloud
#lsClient = LaserMind(user_token=user_token)

# Request a LPU solution to the QUBO problem
res = lsClient.solve_qubo_lpu(matrixData = quboProblemData, num_runs=2)

assert 'data' in res
assert "solutions" in res['data'], "Test FAILED, response is not in expected format"

print(f"Test PASSED, response is: \n{res}")


# Connect to the LightSolver Cloud
lsClient = LaserMind(userToken=user_token)



res = lsClient.get_account_details()

assert 'username' in res
assert 'dlpu_spin_limit' in res
assert 'expiration_date' in res
assert 'dlpu_credit_seconds' in res

print(f"Test PASSED, response is: \n{res}")
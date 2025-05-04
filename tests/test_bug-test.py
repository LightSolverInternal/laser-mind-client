import numpy
from laser_mind_client_meta import MessageKeys
from laser_mind_client import LaserMind

import os
def test_env():
    os.environ["LS_API_RUN_URL"] = "http://dev.internal.lightsolver.com/api/v1/commands/run"
    os.environ["LS_API_RUN_SECURED_URL"] = "https://devfront.internal.lightsolver.com/api/v1/commands/run"
    os.environ["LS_AUTH_URL"] = "https://auth.devfront.lightsolver.com/authorize-solver-usage"
    os.environ["LS_REQUEST_URL"] = "https://devfront.internal.lightsolver.com/api/v1/getsolution-with-status"
    os.environ["LS_API_GET_PRESIGNED_URL"] = "https://devfront.internal.lightsolver.com/api/v1/getposturl"

def set_prod_env_vars():
    os.environ["LS_API_RUN_URL"] = "http://solve.lightsolver.com/api/v1/commands/run"
    os.environ["LS_API_RUN_SECURED_URL"] = "https://solve.lightsolver.com/api/v1/commands/run"
    os.environ["LS_AUTH_URL"] = "https://auth.devfront.lightsolver.com/authorize-solver-usage"
    os.environ["LS_REQUEST_URL"] = "https://solve.lightsolver.com/api/v1/getsolution"
    os.environ["LS_API_GET_PRESIGNED_URL"] = "https://solve.lightsolver.com/api/v1/getposturl"

user_token = "f4ALtwB+zTt1lXJKZdtpIP9lliJUY8I9Oj7W+plCWw6NS3t4nT2aQcF/7scNWCbwNm79sY+acj5SbuToC4bTunyGtmGtDn2qkse1fzz0Y/9LDqxL/P4U/CtkD0qeFDGI"


def get_X_light_computer(timeout=60):
    # Create a mock QUBO problem
    quboProblemData = numpy.random.randint(-1, 2, (10, 10))
    # Symmetrize the matrix
    quboProblemData = (quboProblemData + quboProblemData.T) // 2
    print(quboProblemData)

    # Connect to the LightSolver Cloud
    lsClient = LaserMind(user_token=user_token)
    print("ajksfhasfasfklj")
    res = lsClient.solve_qubo(matrix_data = quboProblemData, timeout=timeout)

    assert MessageKeys.SOLUTION in res, "Test FAILED, response is not in expected format"

    print(f"Test PASSED, response is: \n{res}")
    return res.get('solution')

set_prod_env_vars()
get_X_light_computer()

# This is a basic sanity test for the LaserMind cloud solver
# We will create a small random QUBO problem and request a solution from the LightSolver cloud

# Keep in mind that the following is a test function for using with a testing framework.
# This project comes with a VSCode + pytest testing configuration.
# To run this test with VSCode, click on the "Testing" pane to find it.

# In order to easily create our input, we will use numpy
import numpy

# We also need to import the LaserMind class from the laser_mind_client module
from laser_mind_client import LaserMind


def test_qubo_full_sanity():
    # create our input data
    quboProblemData = numpy.random.randint(-1, 2, (10,10))

    # symmetrize our matrix
    quboProblemData = (quboProblemData + quboProblemData.T) // 2

    # create an instance of the LaserMind class
    lsClient = LaserMind()

    # solve our QUBO problem using the LightSolver cloud
    res = lsClient.solve_qubo(matrixData = quboProblemData, timeout=1)

    # assert that we got the expected outcome
    assert 'solution' in res.keys(), "no solution in result"
    assert 'objval' in res.keys(), "no objval in result"

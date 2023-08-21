import os
import numpy
import pytest

from laser_mind_client import LaserMind

@pytest.fixture(autouse=True)
def run_before():
    global lsClient
    lsClient = LaserMind(*get_creds())

quboProblemData = numpy.random.randint((10,10))

def test_qubo_full_sanity():
    res = lsClient.solve_qubo_full(matrixData = quboProblemData, timeout=1)
    assert 'solution' in res.keys(), "no solution in result"
    assert 'objval' in res.keys(), "no objval in result"

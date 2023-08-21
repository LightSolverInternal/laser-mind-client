import os
import numpy
import pytest
import time


from laser_mind_client import LaserMind
from laser_mind_meta import MessageKeys

@pytest.fixture(autouse=True)
def run_before():
    global lsClient
    lsClient = LaserMind()

def create_nn_edgeList(varCount):
    items = [[x,x,1] for x in range(1, varCount + 1)]
    items += [[x,x+1,1] for x in range(1, varCount)]
    return items

@pytest.mark.dev_tests
def test_qubo_full_2K_spins():
    # create matrix
    largeMatrix = numpy.random.randint(-1,2, (2000,2000))
    # symmetrize (CPU algo constraint)
    largeMatrix = (largeMatrix + largeMatrix.T)
    start = time.time()
    res = lsClient.solve_qubo_full(matrixData = largeMatrix, timeout=1)
    total = time.time() - start
    print(f"{total=}")
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

@pytest.mark.dev_tests
def test_qubo_full_4K_spins():
    # create matrix
    largeMatrix = numpy.random.randint(-1,2, (4000,4000))
    # symmetrize (CPU algo constraint)
    largeMatrix = (largeMatrix + largeMatrix.T)

    start = time.time()
    res = lsClient.solve_qubo_full(matrixData = largeMatrix, timeout=1)
    total = time.time() - start
    print(f"{total=}")
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

@pytest.mark.dev_tests
def test_qubo_full_5K_spins():
    # create matrix
    largeMatrix = numpy.random.randint(-1,2, (5000,5000))
    # symmetrize (CPU algo constraint)
    largeMatrix = (largeMatrix + largeMatrix.T)

    start = time.time()
    res = lsClient.solve_qubo_full(matrixData = largeMatrix, timeout=1)
    total = time.time() - start
    print(f"{total=}")
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"


@pytest.mark.dev_tests
def test_qubo_full_8K_spins():
    # create matrix
    largeMatrix = numpy.random.randint(-1,2, (8000,8000))
    # symmetrize (CPU algo constraint)
    largeMatrix = (largeMatrix + largeMatrix.T)

    start = time.time()
    res = lsClient.solve_qubo_full(matrixData = largeMatrix, timeout=1)
    total = time.time() - start
    print(f"{total=}")
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

@pytest.mark.dev_tests
def test_qubo_full_10K_spins():
    # create matrix
    largeMatrix = numpy.random.randint(-1,2, (10000,10000))
    # symmetrize (CPU algo constraint)
    largeMatrix = (largeMatrix + largeMatrix.T)

    start = time.time()
    res = lsClient.solve_qubo_full(matrixData = largeMatrix, timeout=1)
    total = time.time() - start
    print(f"{total=}")
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

@pytest.mark.dev_tests
def test_qubo_full_2K_spins_nn_edgeList():
    edges = create_nn_edgeList(2000)
    res = lsClient.solve_qubo_full(edgeList=edges, timeout=1)
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

@pytest.mark.dev_tests
def test_qubo_full_4K_spins_nn_edgeList():
    edges = create_nn_edgeList(4000)
    res = lsClient.solve_qubo_full(edgeList=edges, timeout=1)
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

@pytest.mark.dev_tests
def test_qubo_full_5K_spins_nn_edgeList():
    edges = create_nn_edgeList(5000)
    res = lsClient.solve_qubo_full(edgeList=edges, timeout=1)
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

@pytest.mark.dev_tests
def test_qubo_full_8K_spins_nn_edgeList():
    edges = create_nn_edgeList(8000)
    res = lsClient.solve_qubo_full(edgeList=edges, timeout=1)
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

@pytest.mark.dev_tests
def test_qubo_full_10K_spins_nn_edgeList():
    edges = create_nn_edgeList(10000)
    res = lsClient.solve_qubo_full(edgeList=edges, timeout=1)
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

@pytest.mark.dev_tests
def test_qubo_full_12K_spins_nn_edgeList():
    edges = create_nn_edgeList(12000)
    res = lsClient.solve_qubo_full(edgeList=edges, timeout=1)
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

@pytest.mark.dev_tests
def test_qubo_full_14K_spins_nn_edgeList():
    edges = create_nn_edgeList(14000)
    res = lsClient.solve_qubo_full(edgeList=edges, timeout=1)
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

@pytest.mark.dev_tests
def test_qubo_full_16K_spins_nn_edgeList():
    edges = create_nn_edgeList(16000)
    res = lsClient.solve_qubo_full(edgeList=edges, timeout=1)
    assert len(res['data'][MessageKeys.SOLUTIONS]) == 7, "wrong solution count"
    for s in res['data'][MessageKeys.SOLUTIONS]:
        assert 'objval' in s.keys() , f"no objval for solution: {s}"

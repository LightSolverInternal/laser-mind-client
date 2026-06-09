import os
import sys
from pathlib import Path

import numpy as np
import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from laser_mind_client import LaserMind


def _client() -> LaserMind:
    token = os.getenv("LASER_MIND_TOKEN")
    if not token:
        pytest.skip("LASER_MIND_TOKEN is required for smoke tests")
    return LaserMind(userToken=token)


def _small_qubo(size: int = 10) -> np.ndarray:
    mat = np.eye(size, dtype=np.int32)
    for i in range(size - 1):
        mat[i, i + 1] = -1
        mat[i + 1, i] = -1
    return mat


def _small_coupmat(size: int = 5) -> np.ndarray:
    mat = 0.5 * np.eye(size, dtype=np.complex64)
    coupling = np.float32(0.25)
    for i in range(size - 1):
        mat[i, i + 1] = coupling
        mat[i + 1, i] = coupling
    return mat


def _small_magentax_payload() -> dict:
    n_rows = np.int32(2)
    n_cols = np.int32(2)
    n_connectivity = np.int32(1)
    shape = (int(n_rows), int(n_cols), int(n_connectivity))

    return {
        "n_rows": n_rows,
        "n_cols": n_cols,
        "n_connectivity": n_connectivity,
        "coupling_offset_cols": np.array([0], dtype=np.int32),
        "coupling_offset_rows": np.array([0], dtype=np.int32),
        "coupling_amplitude": np.ones(shape, dtype=np.float32),
        "coupling_phase": np.zeros(shape, dtype=np.float32),
        "initial_field_amplitude": np.ones((int(n_rows), int(n_cols)), dtype=np.float32),
        "initial_field_phase": np.zeros((int(n_rows), int(n_cols)), dtype=np.float32),
        "initial_gain": np.full((int(n_rows), int(n_cols)), 1.65, dtype=np.float32),
        "random_noise_seed": np.uint64(0),
        "n_rounds": np.int32(10),
        "n_sampled": np.int32(1),
        "sampled_index_cols": np.array([0], dtype=np.int32),
        "sampled_index_rows": np.array([0], dtype=np.int32),
        "sampling_period": np.int32(1),
        "fourier_n": np.int32(4),
        "fourier_f1": np.int32(1),
        "pump_max": np.float32(2.2),
        "pump_tau": np.float32(100.0),
        "pump_threshold": np.float32(1.8),
        "pump_const": np.float32(0.0006),
        "gain_saturation": np.float32(1.0),
        "amplitude_noise": np.float32(0.0),
    }


def test_dlpu() -> None:
    client = _client()
    res = client.solve_qubo(matrixData=_small_qubo(), timeout=1)
    assert "solution" in res
    assert "objval" in res
    assert len(res["solution"]) == 10


def test_lpu_cyan() -> None:
    client = _client()
    res = client.solve_coupling_matrix_lpu(matrixData=_small_coupmat(), num_runs=1)
    assert "data" in res
    assert "solutions" in res["data"]
    assert len(res["data"]["solutions"]) == 1
    assert "phase_problem" in res["data"]["solutions"][0]


def test_lpu_cyan_x() -> None:
    client = _client()
    res = client.solve_coupling_matrix_sim_lpu(
        matrix_data=_small_coupmat(),
        num_runs=1,
        num_iterations=5,
        rounds_per_record=1,
    )
    assert "data" in res
    assert "result" in res["data"]
    assert "start_states" in res["data"]["result"]
    assert len(res["data"]["result"]["start_states"]) == 1


def test_lpu_magenta_x() -> None:
    client = _client()
    res = client.solve_magentax(input_payload=_small_magentax_payload())
    assert "output" in res
    assert "execution_metadata" in res
    assert "final_phase" in res["output"]

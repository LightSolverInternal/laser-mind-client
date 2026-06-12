import numpy as np

import laser_mind_client.laser_mind_client as lm_module
from laser_mind_client import LaserMind
from laser_mind_client_meta import MessageKeys


class _ApiClientRecorder:
    def __init__(self, *args, **kwargs):
        self.calls = []
        self.upload_calls = 0

    def upload_command_input(self, command_input, input_path=None):
        self.upload_calls += 1
        return f"iid-{self.upload_calls}"

    def SendCommandRequest(self, command_name, request_input):
        self.calls.append((command_name, request_input))
        return {"command": command_name, "request_input": request_input}


def _client(monkeypatch):
    monkeypatch.setattr(lm_module, "LSAPIClient", _ApiClientRecorder)
    return LaserMind(userToken="unit-test-token", logToFile=False, logToConsole=False)


def test_lpu_cyan_x_coupmat_top_level_io(monkeypatch):
    client = _client(monkeypatch)

    out = client.solve_lpu_cyan_x(matrix_data=np.eye(2, dtype=np.complex64), waitForSolution=False)
    command, request_input = client.apiClient.calls[-1]

    assert command == "SIMLPUSolver_Coupmat"
    assert request_input[MessageKeys.QUBO_INPUT_PATH] == "iid-1"
    assert request_input[MessageKeys.VAR_COUNT_KEY] == 2
    assert out["command"] == "SIMLPUSolver_Coupmat"


def test_lpu_cyan_coupmat_top_level_io(monkeypatch):
    client = _client(monkeypatch)

    out = client.solve_lpu_cyan(matrixData=np.eye(2, dtype=np.complex64), waitForSolution=False)
    command, request_input = client.apiClient.calls[-1]

    assert command == "LPUSolver_Coupmat"
    assert request_input[MessageKeys.QUBO_INPUT_PATH] == "iid-1"
    assert request_input[MessageKeys.VAR_COUNT_KEY] == 2
    assert out["command"] == "LPUSolver_Coupmat"


def test_lpu_cyan_scan_top_level_io(monkeypatch):
    client = _client(monkeypatch)

    out = client.solve_lpu_cyan_scan(matrixData=np.eye(2, dtype=np.complex64), waitForSolution=False)
    command, request_input = client.apiClient.calls[-1]

    assert command == "LPUSolver_ScanProblem"
    assert request_input[MessageKeys.QUBO_INPUT_PATH] == "iid-1"
    assert request_input[MessageKeys.VAR_COUNT_KEY] == 2
    assert out["command"] == "LPUSolver_ScanProblem"


def test_magentax_top_level_io_minimal(monkeypatch):
    client = _client(monkeypatch)
    payload = {"n_rows": np.int32(2), "n_cols": np.int32(2)}

    out = client.solve_magentax(input_payload=payload, waitForSolution=False)
    command, request_input = client.apiClient.calls[-1]

    assert command == "Solver_MAGENTAX"
    assert request_input[MessageKeys.QUBO_INPUT_PATH] == "iid-1"
    assert request_input[MessageKeys.VAR_COUNT_KEY] == 4
    assert out["command"] == "Solver_MAGENTAX"

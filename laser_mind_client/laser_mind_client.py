import os
import logging
import time
import numpy
import requests

from ls_api_clients import LSAPIClient
from ls_packers import float_array_as_int
from ls_packers import numpy_array_to_triu_flat
from laser_mind_client_meta import MessageKeys


import base64
import io

def numpy_to_npz_b64(**matrices) -> str:
    # usage: numpy_to_npz_b64(phase=phase, amplitude=ampl)
    out_matrix_npz_b64 = ""
    try:
        buf = io.BytesIO()
        numpy.savez(buf, **matrices)
        buf.seek(0)
        out_matrix_npz_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception as e :
        raise e
    return out_matrix_npz_b64


def npz_b64_to_python(npz_b64: str) :
    """
    Decode base64-encoded .npz created by numpy_to_npz_b64()
    and return a dict
    """
    if not npz_b64:
        return {}
    raw = base64.b64decode(npz_b64)
    buf = io.BytesIO(raw)
    out = {}
    with numpy.load(buf, allow_pickle=True) as data:
        for key in data.files:
            v = data[key]
            # Restore Python scalar if it was saved as 0-D ndarray
            if isinstance(v, numpy.ndarray) and v.ndim == 0:
                out[key] = v.item()
            else:
                out[key] = v
    return out

from pathlib import Path



def build_file_logger():
    internal_logger: logging.Logger | None = None
    log_file = Path("laser-mind.log")
    internal_logger = logging.getLogger("CLIENT.internal")
    internal_logger.setLevel(logging.DEBUG)
    internal_logger.propagate = False
    internal_logger.handlers.clear()

    internal_file_handler = logging.FileHandler(log_file, encoding="utf-8")
    internal_file_handler.setLevel(logging.DEBUG)
    internal_file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s", datefmt='%m/%d/%Y %H:%M:%S')
    )
    internal_logger.addHandler(internal_file_handler)
    return internal_logger


def build_console_logger():
    client_logger: logging.Logger | None = None
    client_logger = logging.getLogger("my_package.client")
    client_logger.setLevel(logging.INFO)
    client_logger.propagate = False
    client_logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    client_logger.addHandler(console_handler)
    return client_logger


def symmetrize(matrix):
        """
        Symmetrizes a given matrix in numpy array form
        """
        if (matrix == matrix.T).all():
        # do nothing if the matrix is already symmetric
            return matrix
        result = (matrix + matrix.T) * 0.5
        return result

class LaserMind:
    """
    ## A client for accessing LightSolver's computaion capabilities via web services.
    """
    POLL_MAX_RETRIES = 100000
    POLL_DELAY_SECS = 0.5

    def raise_exception(self, message) -> None:
        msg = str(message)
        self.internal_logger.exception(msg)
        if self.client_logger:
            self.client_logger.error(msg)
        raise Exception(msg)

    def raise_ValueError_exception(self, message) -> None:
        msg = str(message)
        self.internal_logger.exception("ValueError: %s",msg)
        if self.client_logger:
            self.client_logger.error("ValueError: %s",msg)
        raise ValueError(msg)

    def raise_TypeError_exception(self, message) -> None:
        msg = str(message)
        self.internal_logger.exception("TypeError: %s",msg)
        if self.client_logger:
            self.client_logger.error("TypeError: %s",msg)
        raise TypeError(msg)

    def _write_info_to_console(self, message: str, *args) -> None:
        if self.client_logger and self.logToConsole:
            self.client_logger.info(message, *args)

    def _write_info_to_file(self, message: str, *args) -> None:
        if self.internal_logger  and self.logToFile:
            self.internal_logger.info(message, *args)


    def __init__(self,
                 userToken=None,
                 pathToRefreshTokenFile=None,
                 logToFile=True,
                 logToConsole=True,
                 file_logger = None,
                 console_logger =None):

        refresh_token = None

        self.logToFile = logToFile
        self.logToConsole = logToConsole

        if not file_logger:
            # Internal logger: file only, optional
            file_logger: logging.Logger | None = None
            if logToFile:
                file_logger = build_file_logger()
        self.internal_logger = file_logger

        if not console_logger:
            # Client logger: console only, optional
            console_logger: logging.Logger | None = None
            if logToConsole:
                console_logger = build_console_logger()
        self.client_logger = console_logger

        if pathToRefreshTokenFile:
            if os.path.exists(pathToRefreshTokenFile):

                    refresh_token = file.read()
            else:
                self.raise_exception("The pathToRefreshTokenFile parameter is expected to point to a valid file.")
        self._write_info_to_console("Authenticating . . . ")
        try:
            self.apiClient = LSAPIClient(usertoken = userToken, refresh_token = refresh_token, logToFile = logToFile, logToConsole = logToConsole)
            self._write_info_to_console("✓ Succesfully connected")
        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud. !!!!!")
        except Exception as e:
            self.raise_exception(e)

    def get_solution_by_id(self, solutionId, timestamp):
        """
        Retrieve a previously requested solution from the LightSolver cloud.

        - `solutionId` : the solution id received when requesting a solution.
        - `timestamp` : the timestamp received when requesting a solution.
        """
        result, status  = self.apiClient.SendResultRequest(solutionId, timestamp)
        return result, status

    def post_processing (self, result):
        if 'data' not in result:
            return result
        if "method" in result['data']:
            if result['data']["method"] == "solve_coupling_matrix_lpu":
                num_runs = result['data']["num_runs"]
                solutions_result = npz_b64_to_python (result['data']['solutions'])
                result['data']['solutions'] = []
                for idx in range (num_runs):
                    solution = {'phase_problem':solutions_result['phase_problem'][idx],
                                'phase_reference':solutions_result['phase_reference'][idx],
                                'energy_problem':solutions_result['energy_problem'][idx],
                                'energy_reference':solutions_result['energy_reference'][idx],
                                'contrast_problem':solutions_result['contrast_problem'][idx],
                                'contrast_reference':solutions_result['contrast_reference'][idx],
                                'image_problem_list':solutions_result['image_problem_list'][idx],
                                'image_reference_list':solutions_result['image_reference_list'][idx],
                                'snr_problem':solutions_result['snr_problem'][idx],
                                'snr_reference':solutions_result['snr_reference'][idx],
                                'solverRunningTime': result['data']["solver_running_time"]
                                }
                    result['data']['solutions'].append(solution)

                if 'effective_coupmat' in solutions_result:
                    result['effective_coupmat'] = solutions_result['effective_coupmat']

                if "warnings" in solutions_result:
                    result["warnings"] = solutions_result["warnings"]

                if "validation_warnings" in solutions_result:
                    result["validation_warnings"] = solutions_result["validation_warnings"]

                return result

            elif result['data']["method"] == "solve_scan_lpu":
                solutions_result = npz_b64_to_python (result['data']['solutions'])

                result['data']['solutions'] = []
                num_of_steps = result['data']['num_of_steps']
                for idx in range (result['data']["num_runs"]):
                    run_solutions = []
                    for step in range (num_of_steps):
                        solution_step = {'phase_problem':solutions_result['phase_problem'][idx][step],
                                    'phase_reference':solutions_result['phase_reference'][idx][step],
                                    'energy_problem':solutions_result['energy_problem'][idx][step],
                                    'energy_reference':solutions_result['energy_reference'][idx][step],
                                    'contrast_problem':solutions_result['contrast_problem'][idx][step],
                                    'contrast_reference':solutions_result['contrast_reference'][idx][step],
                                    'image_problem_list':solutions_result['image_problem_list'][idx][step],
                                    'image_reference_list':solutions_result['image_reference_list'][idx][step],
                                    'snr_problem':solutions_result['snr_problem'][idx][step],
                                    'snr_reference':solutions_result['snr_reference'][idx][step]
                                    }
                        run_solutions.append(solution_step)
                    result['data']['solutions'].append(run_solutions)

                if 'effective_coupmat' in solutions_result:
                    result['effective_coupmat'] = solutions_result['effective_coupmat']

                if "warnings" in solutions_result:
                    result["warnings"] = solutions_result["warnings"]

                if "validation_warnings" in result['data']:
                    result["validation_warnings"] = result['data']["validation_warnings"]

                if "exposure_time" in result['data']:
                    result["exposure_time"] = result['data']["exposure_time"]

                return result

            elif result['data']["method"]  == "solve_coupling_matrix_sim_lpu":
                solutions_result = npz_b64_to_python (result['data']['result'])
                # Reconstruct arrays
                result['data']['result'] = {}
                result['data']['result']['start_states'] = solutions_result['start_states'].tolist()
                result['data']['result']['final_states'] = solutions_result['final_states'].tolist()
                result['data']['result']['final_gains']  = solutions_result['final_gains'].tolist()
                result['data']['result']['record_states']= solutions_result['record_states']
                result['data']['result']['record_gains'] = solutions_result['record_gains']
                result['data']['result']['num_runs']     = solutions_result["num_runs"]
                result['data']['result']['solver_time'] = solutions_result['solver_time']
                return result

            elif result['data']["method"] == "solve_magentax":
                solutions_result = npz_b64_to_python (result['data']['result'])
                return solutions_result

        return result

    def get_solution_sync(self, requestInfo):
        """
        Waits for a solution to be available and downloads it.

        - `requestInfo` : a dictionary containing 'id' and 'reqTime' keys needed for retrieving the solution.
        """

        request_id = requestInfo["id"]
        request_time = requestInfo["reqTime"]

        self._write_info_to_file("getting solution: %s ...",f"{request_id}_{request_time}")

        last_status = None
        for try_num in range(1, self.POLL_MAX_RETRIES):
            result, status = self.get_solution_by_id(request_id, request_time)

            if status is not None and status != last_status:
                self._write_info_to_file(
                    "Solution status changed to %s, for %s_%s",
                    status,
                    request_id,
                    request_time,
                )
                self._write_info_to_console("Solution status changed to %s", status)
                last_status = status

            if result != None:
                result["receivedTime"] = requestInfo["receivedTime"]
                self._write_info_to_file(f"got solution for {requestInfo}, try #{try_num}")
                self._write_info_to_console("✓ Solution received " )

                return self.post_processing(result)
            time.sleep((self.POLL_DELAY_SECS))

        self.raise_exception(f"Exceeded max retries when attempting to find {requestInfo['id']}")


    def make_command_input(self, matrixData = None, edgeList = None, timeout = 10):
        """
        Creates the message payload for a request input.
        """
        commandInput = {}

        if matrixData is not None:
            varCount = len(matrixData)
            if varCount > 10000 or varCount < 10:
                self.raise_ValueError_exception("The total number of variables must be between 10-10000")
            if type(matrixData) == numpy.ndarray:
                matrixData = symmetrize(matrixData)
                if matrixData.dtype == numpy.float32 or matrixData.dtype == numpy.float64:
                    triuFlat = float_array_as_int(numpy_array_to_triu_flat(matrixData))
                    commandInput[MessageKeys.FLOAT_DATA_AS_INT] = True
                else:
                    triuFlat = numpy_array_to_triu_flat(matrixData)
            else:
                validationArr = [len(matrixData[i]) != varCount for i in range(varCount)]
                if numpy.array(validationArr).any():
                    self.raise_ValueError_exception("The input must be a square matrix")
                triuFlat = numpy_array_to_triu_flat(symmetrize(numpy.array(matrixData)))
            commandInput[MessageKeys.QUBO_MATRIX] = triuFlat.tolist()
        elif edgeList is not None:
            if type(edgeList) == numpy.ndarray:
                varCount = numpy.max(edgeList[:,0:2])
                edgeList = edgeList.tolist()
            else:
                varCount = numpy.max(numpy.array(edgeList)[:,0:2])
            if varCount > 10000 or varCount < 10:
                self.raise_ValueError_exception("The total number of variables must be between 10-10000")
            commandInput[MessageKeys.QUBO_EDGE_LIST] = edgeList
        else:
            self.raise_ValueError_exception("You must provide either a QUBO matrix or a QUBO edge list")

        commandInput[MessageKeys.ALGO_RUN_TIMEOUT] = timeout
        return commandInput, int(varCount)

    def upload_qubo_input(self, matrixData = None, edgeList = None, timeout = 10, inputPath = None):
        """
        Uploads the given input to the lightsolver cloud for later processing.

        - `matrixData` : (optional) The matrix data of the target problem, must be a symmetric matrix. if given, the edge list in the vortex parameters is ignored.
        - `edgeList` : (optional) The edge list describing Ising matrix of the target problem. if the matrixData parameter is given, this parameter is ignored.
        - `timeout` : (optional) the running timeout, in seconds for the algorithm, must be in the range 0.001 - 60 (default: 10).
        - `inputPath` : (optional) The the path to a pre-uploaded input file if not given a random string is used returned.

        Returns a dictionary with the 'data' key being a dictionary representing the solution using the following keys:
        - `iid` : The id of the uploaded file.
        - `varCount` : The amount number of variables of the problem.

        """
        try:
            commandInput, varCount = self.make_command_input(matrixData, edgeList, timeout)

            iid = self.apiClient.upload_command_input(commandInput, inputPath)
            return iid, varCount
        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud. !!!!!")
        except Exception as e:
            self.raise_exception(e)

    def solve_qubo(self, matrixData = None, edgeList = None, inputPath = None, timeout = 10, waitForSolution = True):
        """
        Solves a qubo problem using the optimized algorithm.

        - `matrixData` : (optional) The matrix data of the target problem, must be a symmetric matrix. if given, the edge list in the vortex parameters is ignored.
        - `edgeList` : (optional) The edge list describing Ising matrix of the target problem. if the matrixData parameter is given, this parameter is ignored.
        - `inputPath` : (optional) The the path to a pre-uploaded input file, the upload can be done using the upload_qubo_input() method of this class.
        - `timeout` : (optional) the running timeout, in seconds for the algorithm, must be in the range 0.001 - 60 (default: 10).
        - `waitForSolution` : (optional) When set to True it waits for the solution, else returns with retrieval info (default: True).

        Returns a dictionary with the 'data' key being a dictionary representing the solution using the following keys:
        - `objval` : The objective value.
        - `solution` : The optimal solution found.
        """
        command_name = MessageKeys.QUBO_COMMAND_NAME
        if inputPath == None:
            iid, varCount = self.upload_qubo_input(matrixData, edgeList, timeout)
        else:
            iid = inputPath
            varCount = 10000

        requestInput = {
            MessageKeys.QUBO_INPUT_PATH : iid,
            MessageKeys.ALGO_RUN_TIMEOUT : timeout,
            MessageKeys.VAR_COUNT_KEY : varCount
            }
        try:
            self._write_info_to_console("Submitting job..." )
            response = self.apiClient.SendCommandRequest(command_name, requestInput)
            self._write_info_to_file("Submitting job done , response %s" , response)
            self._write_info_to_console("Processing..." )
            if not waitForSolution:
                return response
            result = self.get_solution_sync(response)
            return result
        except requests.exceptions.ConnectionError as e:
            self.raise_exceptionn("!!!!! No access to LightSolver Cloud. !!!!!")
        except Exception as e:
            self.raise_exception(e)


    def get_account_details(self):
        requestInput = {}
        try:
            self._write_info_to_console("Submitting job..." )
            response = self.apiClient.SendCommandRequest("get_account_details", requestInput)
        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, WEB server !!!!!")
        except Exception as e:
            self.raise_exception(e)
        self._write_info_to_file("Submitting job done , response %s" , response)
        self._write_info_to_console("Processing..." )
        return response


    def solve_qubo_lpu(self, matrixData = None, edgeList = None, waitForSolution = True, inputPath = None, num_runs = 1 ):
        if inputPath == None:
            iid, varCount = self.upload_lpu_qubo_input(matrix_data = matrixData, edge_list = edgeList)
        else:
            iid = inputPath
            varCount = 100

        requestInput = {
            MessageKeys.QUBO_INPUT_PATH : iid,
            MessageKeys.VAR_COUNT_KEY : varCount,
            MessageKeys.LPU_NUM_RUNS : num_runs
            }

        try:
            self._write_info_to_console("Submitting job..." )
            response = self.apiClient.SendCommandRequest("LPUSolver_QUBOFull", requestInput)
        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, WEB server !!!!!")
        except Exception as e:
            self.raise_exception(e)

        self._write_info_to_file("Submitting job done , response %s" , response)
        self._write_info_to_console("Processing..." )

        if not waitForSolution:
            return response

        try:
            result = self.get_solution_sync(response)
            return result
        except requests.exceptions.ConnectionError   as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, SOLUTION server !!!!!")
        except Exception as e:
            self.raise_exception(e)


    def solve_coupling_matrix_lpu(self,
                                  matrixData = None,
                                  edgeList = None,
                                  waitForSolution = True,
                                  inputPath = None,
                                  num_runs = 1,
                                  average_over = 1,
                                  exposure_time= None,
                                  num_neighbors = 1,
                                  effective_coupmat_translation_accuracy = 10.0,
                                  effective_coupmat_translation_time = 0.0
                                  ):
        if inputPath == None:
            iid, varCount = self.upload_lpu_coupmat_input(matrix_data= matrixData, edge_list = edgeList)
        else:
            iid = inputPath
            varCount = 100

        requestInput = {
            MessageKeys.QUBO_INPUT_PATH : iid,
            MessageKeys.VAR_COUNT_KEY : varCount,
            MessageKeys.LPU_NUM_RUNS : num_runs,
            MessageKeys.LPU_AVERAGE_OVER : average_over,
            MessageKeys.LPU_COUPMAT_NUM_NEIGHBORS : num_neighbors,
            MessageKeys.LPU_COUPMAT_ETA : effective_coupmat_translation_accuracy,
            MessageKeys.LPU_COUPMAT_ETT : effective_coupmat_translation_time
            }

        if exposure_time:
             requestInput[MessageKeys.LPU_COUPMAT_EXPOSURE_MUS] =  int(exposure_time)

        try:
            self._write_info_to_console("Submitting job..." )
            response = self.apiClient.SendCommandRequest("LPUSolver_Coupmat", requestInput)
        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, WEB server !!!!!")
        except Exception as e:
            self.raise_exception(e)

        self._write_info_to_file("Submitting job done , response %s" , response)
        self._write_info_to_console("Processing..." )

        if not waitForSolution:
            return response
        try:
            result = self.get_solution_sync(response)
            return result

        except requests.exceptions.ConnectionError   as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, SOLUTION server !!!!!")
        except Exception as e:
            self.raise_exception(e)

    def upload_lpu_qubo_input(self, matrix_data = None, edge_list = None, input_path = None):
        command_input = {}
        if matrix_data is not None:
            var_count = len(matrix_data)

            if type(matrix_data) == numpy.ndarray:
                matrix_data = symmetrize(matrix_data)
                if matrix_data.dtype == numpy.float32 or matrix_data.dtype == numpy.float64:
                    triu_flat = float_array_as_int(numpy_array_to_triu_flat(matrix_data))
                    command_input[MessageKeys.FLOAT_DATA_AS_INT] = True
                else:
                    triu_flat = numpy_array_to_triu_flat(matrix_data)
            else:
                validationArr = [len(matrix_data[i]) != var_count for i in range(var_count)]
                if numpy.array(validationArr).any():
                    self.raise_ValueError_exception("The input must be a square matrix")
                triu_flat = numpy_array_to_triu_flat(symmetrize(numpy.array(matrix_data)))
            command_input[MessageKeys.QUBO_MATRIX] = triu_flat.tolist()

        elif edge_list is not None:
            if type(edge_list) == numpy.ndarray:
                var_count = numpy.max(edge_list[:,0:2])
                edge_list = edge_list.tolist()
            else:
                var_count = numpy.max(numpy.array(edge_list)[:,0:2])
            command_input[MessageKeys.QUBO_EDGE_LIST] = edge_list

        else:
            self.raise_ValueError_exception("You must provide either a QUBO matrix or a QUBO edge list")

        try:
            iid = self.apiClient.upload_command_input(command_input, input_path)
            return iid, int(var_count)
        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, URL PROVIDER server !!!!!")
        except Exception as e:
            self.raise_exception(e)


    def upload_lpu_coupmat_input(self, matrix_data = None, edge_list = None, input_path = None):
        data_input = {}

        if matrix_data is  None:
            self.raise_TypeError_exception("The input matrix must be not empty")
        elif edge_list is not None:
            self.raise_TypeError_exception("Edge List not supported as coup_matrix input")

        if type(matrix_data) != numpy.ndarray:
            self.raise_TypeError_exception("The input must be a numpy array")

        if matrix_data.dtype != numpy.complex64:
            self.raise_TypeError_exception("The input must complex64 type")

        data_input[MessageKeys.COUPMAT_MATRIX] = matrix_data
        var_count = len(matrix_data)

        try:
            command_input={}
            command_input['npz_payload'] = numpy_to_npz_b64(**data_input)
            iid = self.apiClient.upload_command_input(command_input, input_path)
            return iid, int(var_count)

        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, URL PROVIDER server !!!!!")
        except Exception as e:
            self.raise_exception(e)


    def solve_coupling_matrix_sim_lpu(self,
                                      matrix_data  = None,
                                      initial_states_seed = -1,
                                      initial_states_vector = None,
                                      num_runs = 1,
                                      num_iterations = 10000,
                                      rounds_per_record  = 100,
                                      timeout  = 5,
                                      waitForSolution = True,
                                      gain_info_initial_gain = 1.8 ,
                                      gain_info_pump_max = 3 ,
                                      gain_info_pump_tau = 100.0 ,
                                      gain_info_pump_treshold = 1.8 ,
                                      gain_info_amplification_saturation = 1.0 ,
                                      inputPath = None):
        if inputPath == None:
            iid, varCount = self.upload_sim_lpu_coupmat_input(  matrix_data,
                                                                initial_states_seed = initial_states_seed,
                                                                initial_states_vector = initial_states_vector,
                                                                num_runs = num_runs,
                                                                num_iterations = num_iterations,
                                                                rounds_per_record = rounds_per_record,
                                                                timeout  = timeout,
                                                                gain_info_initial_gain = gain_info_initial_gain,
                                                                gain_info_pump_max = gain_info_pump_max ,
                                                                gain_info_pump_tau = gain_info_pump_tau,
                                                                gain_info_pump_treshold = gain_info_pump_treshold ,
                                                                gain_info_amplification_saturation = gain_info_amplification_saturation  )
        else:
            iid = inputPath
            varCount = 100

        requestInput = {
            MessageKeys.QUBO_INPUT_PATH : iid,
            MessageKeys.VAR_COUNT_KEY : varCount,
            MessageKeys.LPU_NUM_RUNS : num_runs
            }

        try:
            self._write_info_to_console("Submitting job..." )
            response = self.apiClient.SendCommandRequest("SIMLPUSolver_Coupmat", requestInput)
        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, WEB server !!!!!")
        except Exception as e:
            self.raise_exception(e)

        self._write_info_to_file("Submitting job done , response %s" , response)
        self._write_info_to_console("Processing..." )

        if not waitForSolution:
            return response

        try:
            result = self.get_solution_sync(response)
            return result
        except requests.exceptions.ConnectionError   as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, SOLUTION server !!!!!")
        except Exception as e:
            self.raise_exception(e)


    def upload_sim_lpu_coupmat_input(self,
                                      matrix_data  = None,
                                      initial_states_seed = -1,
                                      initial_states_vector = None,
                                      num_runs = 1,
                                      num_iterations = 10000,
                                      rounds_per_record  = 100,
                                      timeout  = 5,
                                      gain_info_initial_gain = 1.8 ,
                                      gain_info_pump_max = 3 ,
                                      gain_info_pump_tau = 100.0 ,
                                      gain_info_pump_treshold = 1.8 ,
                                      gain_info_amplification_saturation = 1.0 ,
                                      input_path = None):
        data_input = {}

        if matrix_data is  None:
            self.raise_TypeError_exception("The input matrix must be not empty")

        if type(matrix_data) != numpy.ndarray:
            self.raise_TypeError_exception("The input must be a numpy array")

        if matrix_data.dtype != numpy.complex64:
            self.raise_TypeError_exception("The input must complex64 type")

        data_input[MessageKeys.COUPMAT_MATRIX] = matrix_data
        var_count = len(matrix_data)

        if initial_states_vector is not None:
            if initial_states_vector is not None and num_runs != 1 :
                self.raise_ValueError_exception("initial_states_vector already consist number or runs:{initial_states_vector.shape}")
            if not isinstance(initial_states_vector, numpy.ndarray):
                self.raise_ValueError_exception("initial_states_vector must be a numpy array")
            for i, arr in enumerate(initial_states_vector):
                if not isinstance(arr, numpy.ndarray):
                    self.raise_ValueError_exception(f"Element {i} of initial_states_vector  is not a numpy array")
                if arr.dtype != numpy.complex64:
                    self.raise_ValueError_exception(f"Element {i} of initial_states_vector is not of dtype numpy.complex64")
                if arr.shape[0] != var_count:
                    self.raise_ValueError_exception(f"Element {i} of initial_states_vector does not have size of {var_count}")
            data_input["initial_states"] = initial_states_vector

        if initial_states_vector is not None and initial_states_seed >= 0 :
            self.raise_TypeError_exception("The input must provide only one of seed or vector")
        data_input["initial_states_seed"] = initial_states_seed

        if initial_states_vector is not None and num_runs > 1:
            self.raise_TypeError_exception("For SIM LPU: same initial state vector, run multiple times, will return exactly the same result every time.")

        if num_runs < 1 or num_runs > 10000:
            self.raise_TypeError_exception("The num_runs:{num_runs} in input must be in range 1-10K")
        data_input[MessageKeys.LPU_NUM_RUNS] = num_runs

        if num_iterations < 1 or num_iterations > 200000:
            self.raise_TypeError_exception("The num_iterations:{num_iterations} in  input must be in range 1-200K")
        data_input["num_iterations"] = num_iterations

        if timeout < 1 or timeout > 200000:
            self.raise_TypeError_exception("The timeout:{timeout} in  input must be in range 1-14400 seconds")
        data_input["timeout"] = timeout

        if rounds_per_record < 1 or rounds_per_record > num_iterations:
            self.raise_TypeError_exception("The rounds_per_record :{rounds_per_record} in  input must be in range from 1 to num_iterations:{num_iterations}:")
        data_input["rounds_per_record"] = rounds_per_record

        if gain_info_initial_gain < 0 :
            self.raise_TypeError_exception("The gain_info_initial_gain:{gain_info_initial_gain} in  input must be in range 0-inf ")
        data_input["gain_info_initial_gain"] = gain_info_initial_gain

        if gain_info_pump_max < 0:
            self.raise_TypeError_exception("The gain_info_pump_max:{gain_info_pump_max} in  input must be in range 0-inf")
        data_input["gain_info_pump_max"] = gain_info_pump_max

        if gain_info_pump_tau < 0:
            self.raise_TypeError_exception("The gain_info_pump_tau:{gain_info_pump_tau} in  input must be in range 0-inf")
        data_input["gain_info_pump_tau"] = gain_info_pump_tau

        if gain_info_pump_treshold < 0:
            self.raise_TypeError_exception("The gain_info_pump_treshold:{gain_info_pump_treshold} in  input must be in range 0-inf")
        data_input["gain_info_pump_treshold"] = gain_info_pump_treshold

        if gain_info_amplification_saturation <= 0:
            self.raise_TypeError_exception("The gain_info_amplification_saturation:{gain_info_amplification_saturation} in  input must be in range 0-inf")
        data_input["gain_info_amplification_saturation"] = gain_info_amplification_saturation

        try:
            command_input={}
            command_input['npz_payload'] = numpy_to_npz_b64(**data_input)
            iid = self.apiClient.upload_command_input(command_input, input_path)
            return iid, int(var_count)

        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, URL PROVIDER server !!!!!")
        except Exception as e:
            self.raise_exception(e)


    def upload_solve_scan_lpu_input(self, matrix_data = None, scan_dictionary = None, input_path = None):
        data_input = {}

        if matrix_data is  None:
            self.raise_TypeError_exception("The input matrix must be not empty")

        if type(matrix_data) != numpy.ndarray:
            self.raise_TypeError_exception("The input must be a numpy array")

        if matrix_data.dtype != numpy.complex64:
            self.raise_TypeError_exception("The input must complex64 type")

        data_input[MessageKeys.COUPMAT_MATRIX] = matrix_data

        if scan_dictionary is not None:
            data_input[MessageKeys.SCAN_DICTIONARY] = scan_dictionary
        try:
            command_input={}
            command_input['npz_payload'] = numpy_to_npz_b64(**data_input)
            var_count = len(matrix_data)
            iid = self.apiClient.upload_command_input(command_input, input_path)
            return iid, int(var_count)

        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, URL PROVIDER server !!!!!")
        except Exception as e:
            self.raise_exception(e)


    def solve_scan_lpu( self,
                        matrixData = None,
                        scanDictionary = None,
                        waitForSolution = True,
                        inputPath = None,
                        num_runs = 1,
                        average_over = 1,
                        exposure_time= None,
                        num_neighbors = 1,
                        effective_coupmat_translation_accuracy = 10.0,
                        effective_coupmat_translation_time = 0.0
                        ):
        if inputPath == None:
            iid, varCount = self.upload_solve_scan_lpu_input( matrix_data = matrixData, scan_dictionary = scanDictionary )
        else:
            iid = inputPath
            varCount = 100

        requestInput = {
            MessageKeys.QUBO_INPUT_PATH : iid,
            MessageKeys.VAR_COUNT_KEY : varCount,
            MessageKeys.LPU_NUM_RUNS : num_runs,
            MessageKeys.LPU_AVERAGE_OVER : average_over,
            MessageKeys.LPU_COUPMAT_NUM_NEIGHBORS : num_neighbors,
            MessageKeys.LPU_COUPMAT_ETA : effective_coupmat_translation_accuracy,
            MessageKeys.LPU_COUPMAT_ETT : effective_coupmat_translation_time
            }

        if exposure_time:
             requestInput[MessageKeys.LPU_COUPMAT_EXPOSURE_MUS] =  int(exposure_time)


        try:
            self._write_info_to_console("Submitting job..." )
            response = self.apiClient.SendCommandRequest("LPUSolver_ScanProblem", requestInput)
        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, WEB server !!!!!")
        except Exception as e:
            self.raise_exception(e)

        self._write_info_to_file("Submitting job done , response %s" , response)
        self._write_info_to_console("Processing..." )

        if not waitForSolution:
            return response

        try:
            result = self.get_solution_sync(response)
            return result
        except requests.exceptions.ConnectionError   as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, SOLUTION server !!!!!")
        except Exception as e:
            self.raise_exception(e)


    def solve_magentax(self,
                        input_payload,
                        waitForSolution = True):

        try:
            self.validate_magentax_numpy_dict(input_payload)
        except Exception as e:
            self.raise_exception(e)

        iid, varCount = self.upload_magentax_input(input_payload)

        requestInput = {
            MessageKeys.QUBO_INPUT_PATH : iid,
            MessageKeys.VAR_COUNT_KEY : varCount
            }

        try:
            self._write_info_to_console("Submitting job..." )
            response = self.apiClient.SendCommandRequest("Solver_MAGENTAX", requestInput)
        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, WEB server !!!!!")
        except Exception as e:
            self.raise_exception(e)

        self._write_info_to_file("Submitting job done , response %s" , response)
        self._write_info_to_console("Processing..." )

        if not waitForSolution:
            return response
        try:
            result = self.get_solution_sync(response)
            return result
        except requests.exceptions.ConnectionError   as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, SOLUTION server !!!!!")
        except Exception as e:
            self.raise_exception(e)


    def validate_magentax_numpy_dict(self, input_payload: dict):
        for key, value in input_payload.items():
            if not isinstance(value, (numpy.generic, numpy.ndarray)):
                raise TypeError(
                    f"Parameter '{key}' is not a numpy type. "
                    f"Got type: {type(value).__name__}"
                )


    def upload_magentax_input(self, numpy_dict, input_path=None):
        """Upload a numpy-typed magentax input dictionary. Returns (iid, var_count)."""
        var_count = int(numpy_dict["n_cols"]) * int(numpy_dict["n_rows"])
        try:
            command_input = {}
            command_input['npz_payload'] = numpy_to_npz_b64(**numpy_dict)
            iid = self.apiClient.upload_command_input(command_input, input_path)
            return iid, int(var_count)
        except requests.exceptions.ConnectionError as e:
            self.raise_exception("!!!!! No access to LightSolver Cloud, URL PROVIDER server !!!!!")
        except Exception as e:
            self.raise_exception(e)
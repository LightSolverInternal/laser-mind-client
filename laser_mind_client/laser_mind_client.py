import os
import logging
import time
import numpy
import requests

from ls_api_clients import LSAPIClient
from ls_packers import float_array_as_int
from ls_packers import numpy_array_to_triu_flat
from laser_mind_client_meta import MessageKeys

logging.basicConfig(
    filename="laser-mind.log",
    level=logging.INFO,
    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

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

    def __init__(self,
                 user_token = None,
                 log_to_console=True):
        if user_token is None:
            raise Exception("the 'token' parameter cannot be None ")

        try:
            logging.info('LightSolver connection init started')
            self.apiClient = LSAPIClient(user_token=user_token, log_to_console=log_to_console)
            logging.info('LightSolver connection init finished')
        except requests.exceptions.ConnectionError as e:
            raise Exception("!!!!! No access to LightSolver Cloud. !!!!!")
        except Exception as e:
                raise  e

    def get_solution_by_id(self, solutionId, timestamp):
        """
        Retrieve a previously requested solution from the LightSolver cloud.

        - `solutionId` : the solution id received when requesting a solution.
        - `timestamp` : the timestamp received when requesting a solution.
        """
        result = self.apiClient.SendResultRequest(solutionId, timestamp)
        return result

    def get_solution_sync(self, request_info):
        """
        Waits for a solution to be available and downloads it.

        - `request_info` : a dictionary containing 'id' and 'reqTime' keys needed for retrieving the solution.
        """
        for try_num in range(1, self.POLL_MAX_RETRIES):
            result = self.get_solution_by_id(request_info['id'], request_info['reqTime'])
            if result != None:
                result["receivedTime"] = request_info["receivedTime"]
                logging.info(f"got solution for {request_info}, try #{try_num}")
                return result
            time.sleep((self.POLL_DELAY_SECS))

        logging.warning(f"got timeout for {request_info}")
        raise FileNotFoundError(f"Exceeded max retries when attempting to find {request_info['id']}")

    def make_command_input(self, matrix_data = None, edge_list = None, timeout = 10):
        """
        Creates the message payload for a request input.
        """
        command_input = {}

        if matrix_data is not None:
            var_count = len(matrix_data)
            if var_count > 10000 or var_count < 10:
                raise(ValueError("The total number of variables must be between 10-10000"))
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
                    raise(ValueError("The input must be a square matrix"))
                triu_flat = numpy_array_to_triu_flat(symmetrize(numpy.array(matrix_data)))
            command_input[MessageKeys.QUBO_MATRIX] = triu_flat.tolist()
        elif edge_list is not None:
            if type(edge_list) == numpy.ndarray:
                var_count = numpy.max(edge_list[:,0:2])
                edge_list = edge_list.tolist()
            else:
                var_count = numpy.max(numpy.array(edge_list)[:,0:2])
            if var_count > 10000 or var_count < 10:
                raise(ValueError("The total number of variables must be between 10-10000"))
            command_input[MessageKeys.QUBO_EDGE_LIST] = edge_list
        else:
            raise Exception("You must provide either a QUBO matrix or a QUBO edge list")

        command_input[MessageKeys.ALGO_RUN_TIMEOUT] = timeout
        return command_input, int(var_count)

    def upload_qubo_input(self, matrix_data = None, edge_list = None, timeout = 10, input_path = None):
        """
        Uploads the given input to the lightsolver cloud for later processing.

        - `matrix_data` : (optional) The matrix data of the target problem, must be a symmetric matrix. if given, the edge list in the vortex parameters is ignored.
        - `edge_list` : (optional) The edge list describing Ising matrix of the target problem. if the matrix_data parameter is given, this parameter is ignored.
        - `timeout` : (optional) the running timeout, in seconds for the algorithm, must be in the range 0.001 - 60 (default: 10).
        - `input_path` : (optional) The the path to a pre-uploaded input file if not given a random string is used returned.

        Returns a dictionary with the 'data' key being a dictionary representing the solution using the following keys:
        - `iid` : The id of the uploaded file.
        - `var_count` : The amount number of variables of the problem.

        """
        try:
            command_input, var_count = self.make_command_input(matrix_data, edge_list, timeout)

            iid = self.apiClient.upload_command_input(command_input, input_path)
            return iid, var_count
        except requests.exceptions.ConnectionError as e:
            raise Exception("!!!!! No access to LightSolver Cloud. !!!!!")
        except Exception as e:
                raise  e

    def solve_qubo(self, matrix_data = None, edge_list = None, input_path = None, timeout = 10, wait_for_solution = True):
        """
        Solves a qubo problem using the optimized algorithm.

        - `matrix_data` : (optional) The matrix data of the target problem, must be a symmetric matrix. if given, the edge list in the vortex parameters is ignored.
        - `edge_list` : (optional) The edge list describing Ising matrix of the target problem. if the matrix_data parameter is given, this parameter is ignored.
        - `input_path` : (optional) The the path to a pre-uploaded input file, the upload can be done using the upload_qubo_input() method of this class.
        - `timeout` : (optional) the running timeout, in seconds for the algorithm, must be in the range 0.001 - 60 (default: 10).
        - `wait_for_solution` : (optional) When set to True it waits for the solution, else returns with retrieval info (default: True).

        Returns a dictionary with the 'data' key being a dictionary representing the solution using the following keys:
        - `objval` : The objective value.
        - `solution` : The optimal solution found.
        """
        command_name = MessageKeys.QUBO_COMMAND_NAME
        if input_path == None:
            iid, var_count = self.upload_qubo_input(matrix_data, edge_list, timeout)
        else:
            iid = input_path
            var_count = 10000

        requestInput = {
            MessageKeys.QUBO_INPUT_PATH : iid,
            MessageKeys.ALGO_RUN_TIMEOUT : timeout,
            MessageKeys.VAR_COUNT_KEY : var_count
            }
        try:
            response = self.apiClient.SendCommandRequest(command_name, requestInput)
            logging.info(f"got response {response}")
            if not wait_for_solution:
                return response
            result = self.get_solution_sync(response)
            return result
        except requests.exceptions.ConnectionError as e:
            raise Exception("!!!!! No access to LightSolver Cloud. !!!!!")
        except Exception as e:
                raise  e


    def get_account_details(self):
        requestInput = {}
        try:
            response = self.apiClient.SendCommandRequest("get_account_details", requestInput)
        except requests.exceptions.ConnectionError as e:
            raise  Exception("!!!!! No access to LightSolver Cloud, WEB server !!!!!")
        except Exception as e:
            raise  e
        logging.info(f"got response {response}")
        return response


    def solve_qubo_lpu(self, matrix_data = None, edge_list = None, wait_for_solution = True, input_path = None, num_runs = 1 ):
        if input_path == None:
            iid, var_count = self.upload_lpu_qubo_input(matrix_data, edge_list)
        else:
            iid = input_path
            var_count = 100

        requestInput = {
            MessageKeys.QUBO_INPUT_PATH : iid,
            MessageKeys.VAR_COUNT_KEY : var_count,
            MessageKeys.LPU_NUM_RUNS : num_runs
            }

        try:
            response = self.apiClient.SendCommandRequest("LPUSolver_QUBOFull", requestInput)
        except requests.exceptions.ConnectionError as e:
            raise  Exception("!!!!! No access to LightSolver Cloud, WEB server !!!!!")
        except Exception as e:
            raise  e

        logging.info(f"got response {response}")
        if not wait_for_solution:
            return response

        try:
            result = self.get_solution_sync(response)
            return result
        except requests.exceptions.ConnectionError   as e:
            raise  Exception("!!!!! No access to LightSolver Cloud, SOLUTION server !!!!!")
        except Exception as e:
            raise  e


    def solve_coupling_matrix_lpu(self, matrix_data = None, edge_list = None, wait_for_solution = True, input_path = None, num_runs = 1):
        if input_path == None:
            iid, var_count = self.upload_lpu_coup_matrix_input(matrix_data, edge_list)
        else:
            iid = input_path
            var_count = 100

        requestInput = {
            MessageKeys.QUBO_INPUT_PATH : iid,
            MessageKeys.VAR_COUNT_KEY : var_count,
            MessageKeys.LPU_NUM_RUNS : num_runs
            }

        try:
            response = self.apiClient.SendCommandRequest("LPUSolver_coup_matrix", requestInput)
        except requests.exceptions.ConnectionError as e:
            raise  Exception("!!!!! No access to LightSolver Cloud, WEB server !!!!!")
        except Exception as e:
            raise  e

        logging.info(f"got response {response}")
        if not wait_for_solution:
            return response

        try:
            result = self.get_solution_sync(response)
            return result
        except requests.exceptions.ConnectionError   as e:
            raise  Exception("!!!!! No access to LightSolver Cloud, SOLUTION server !!!!!")
        except Exception as e:
            raise  e


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
                    raise(ValueError("The input must be a square matrix"))
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
            raise (ValueError("You must provide either a QUBO matrix or a QUBO edge list"))

        try:
            iid = self.apiClient.upload_command_input(command_input, input_path)
            return iid, int(var_count)
        except requests.exceptions.ConnectionError as e:
            raise  Exception("!!!!! No access to LightSolver Cloud, URL PROVIDER server !!!!!")
        except Exception as e:
            raise  e


    def upload_lpu_coup_matrix_input(self, matrix_data = None, edge_list = None, input_path = None):
        command_input = {}
        if matrix_data is not None:
            var_count = len(matrix_data)
            if type(matrix_data) == numpy.ndarray:
                if matrix_data.dtype == numpy.complex64:
                    a = matrix_data.flatten()
                    # Combine real and imaginary parts for serialization
                    real_part = a.real.tolist()
                    imag_part = a.imag.tolist()
                    combined = {'real': real_part, 'imag': imag_part,'size':var_count}
                    command_input[MessageKeys.coup_matrix_MATRIX] = combined

                else:
                        raise(ValueError("The input must complex64 type"))
            else:
                raise(ValueError("The input must be a numpy array"))
        elif edge_list is not None:
            raise (ValueError("Edge List not supported as coup_matrix input"))

        try:
            iid = self.apiClient.upload_command_input(command_input, input_path)
            return iid, int(var_count)

        except requests.exceptions.ConnectionError as e:
            raise  Exception("!!!!! No access to LightSolver Cloud, URL PROVIDER server !!!!!")
        except Exception as e:
            raise  e

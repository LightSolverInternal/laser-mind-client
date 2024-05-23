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
                 userToken = None,
                 states_per_call=3):
        if userToken is None:
            raise Exception("the 'token' parameter cannot be None ")

        try:
            self.states_per_call = states_per_call
            logging.info('LightSolver connection init started')
            self.apiClient = LSAPIClient(userToken)
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

    def get_solution_sync(self, requestInfo):
        """
        Waits for a solution to be available and downloads it.

        - `requestInfo` : a dictionary containing 'id' and 'reqTime' keys needed for retrieving the solution.
        """
        for try_num in range(1, self.POLL_MAX_RETRIES):
            result = self.get_solution_by_id(requestInfo['id'], requestInfo['reqTime'])
            if result != None:
                result["receivedTime"] = requestInfo["receivedTime"]
                logging.info(f"got solution for {requestInfo}, try #{try_num}")
                return result
            time.sleep((self.POLL_DELAY_SECS))

        logging.warning(f"got timeout for {requestInfo}")
        raise FileNotFoundError(f"Exceeded max retries when attempting to find {requestInfo['id']}")

    def make_command_input(self, matrixData = None, edgeList = None, timeout = 10):
        """
        Creates the message payload for a request input.
        """
        commandInput = {}

        if matrixData is not None:
            varCount = len(matrixData)
            if varCount > 10000 or varCount < 10:
                raise(ValueError("The total number of variables must be between 10-10000"))
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
                    raise(ValueError("The input must be a square matrix"))
                triuFlat = numpy_array_to_triu_flat(symmetrize(numpy.array(matrixData)))
            commandInput[MessageKeys.QUBO_MATRIX] = triuFlat.tolist()
        elif edgeList is not None:
            if type(edgeList) == numpy.ndarray:
                varCount = numpy.max(edgeList[:,0:2])
                edgeList = edgeList.tolist()
            else:
                varCount = numpy.max(numpy.array(edgeList)[:,0:2])
            if varCount > 10000 or varCount < 10:
                raise(ValueError("The total number of variables must be between 10-10000"))
            commandInput[MessageKeys.QUBO_EDGE_LIST] = edgeList
        else:
            raise Exception("You must provide either a QUBO matrix or a QUBO edge list")

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
            raise Exception("!!!!! No access to LightSolver Cloud. !!!!!")
        except Exception as e:
                raise  e

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
            response = self.apiClient.SendCommandRequest(command_name, requestInput)
            logging.info(f"got response {response}")
            if not waitForSolution:
                return response
            result = self.get_solution_sync(response)
            return result
        except requests.exceptions.ConnectionError as e:
            raise Exception("!!!!! No access to LightSolver Cloud. !!!!!")
        except Exception as e:
                raise  e


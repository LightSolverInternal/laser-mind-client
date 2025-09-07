import numpy as np
import matplotlib.pyplot as plt

from laser_mind_client import LaserMind
from ls_lib_utils import *
from ls_lib import *


# Ising matrix:
I = np.array([[0., 1., 0., 0., 0.],
              [1., 0., 1., 0., 0.],
              [0., 1., 0., 1., 1.],
              [0., 0., 1., 0., 0.],
              [0., 0., 1., 0., 0.]])

coupling_matrix = coupling_matrix_xy(I, XYmodelParams())         # parameters of self-coupling and coupling amplitude 
                                                                 # can be set via XYmodelParams()

# Choosing how to embed a 5 laser problem onto a 15 lasers system 
emedded_coupling_matrix = embedCoupmat(coupling_matrix)

print('Shape of embedded coupling matrix: ', emedded_coupling_matrix.shape)

# Initialize the client
user_token = 'my-personal-token-i-saved-somewhere-i-know-i-did'  # ADD PERSONAL TOKEN HERE
lsClient = LaserMind(userToken=user_token)

# Solve on the LPU:
nRuns = 5       # number of times to repeat the same probelm on the LPU
result_lpu = lsClient.solve_coupling_matrix_lpu(matrixData = emedded_coupling_matrix, num_runs = nRuns)

# Getting the data for n-th run:
n = 0      # looking at run 0, for all lasers
images = np.asarray(result_lpu['data']['solutions'][n]['problem_image'])           
phase_problem = np.asarray(result_lpu['data']['solutions'][n]['phase_problem'])    
phase_reference = np.asarray(result_lpu['data']['solutions'][n]['phase_reference'])
snr_problem = result_lpu['data']['solutions'][n]['snr_problem']
contrast_problem = result_lpu['data']['solutions'][n]['contrast_problem']
contrast_reference = result_lpu['data']['solutions'][n]['contrast_reference']
energy_problem = result_lpu['data']['solutions'][n]['energy_problem']
energy_reference = result_lpu['data']['solutions'][n]['energy_reference']

N = I.shape[0]
phase_diffs_LPU = np.angle(np.exp(1j * phase_problem[:N]) * \
                      np.exp(-1j* phase_reference[:N])).reshape(1, N)   # subtracting reference from problem

# looking at the laser's fringes, for all lasers participating in the problem:
fig, ax = plt.subplots(nrows=1, ncols=N, figsize=(15, 5))
for i in range(I.shape[0]):
    im = ax[i].imshow(images[i, :, :])
    ax[i].axis('off')
    ax[i].set_title(f'{i}')
fig.colorbar(im, ax=ax.ravel().tolist(), orientation='vertical', shrink=0.8)
plt.show(block=False)

result_lpu = lsClient.solve_coupling_matrix_lpu(matrixData=matrixData, num_runs=nRuns, exposure_time=100)

# Analyze the solution from LPU
energy, solution = analyze_sol_XY(I, phase_diffs_LPU)  # notice that matrix 'I' is sent to the function (the original Ising problem, NOT the coupling_matrix!)

print('The minimal energy found by the LPU: ', energy)
print('The corresponding state is: ', solution)
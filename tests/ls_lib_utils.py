import numpy as np

from ls_lib import *

# Utility functions used in ls_lib_physical.py & ls_lib_virtual.py

def embedCoupmat(coupling_matrix, indices=None, total_laser_num=15):
        '''
        Embed a coupling matrix into a larger matrix of size total_laser_num x total_laser_num.
    
        Parameters:
        - coupling_matrix: (N x N) complex matrix to embed
        - indices: list of indices at which to embed the matrix. If None, embed from index 0.
        - total_laser_num: total size of the output matrix (default 15)

        Returns:
        - embedded: (total_laser_num x total_laser_num) matrix with the coupling matrix embedded
        '''
        N = coupling_matrix.shape[0]

        embedded = 0.001 * np.eye(total_laser_num).astype(np.complex64)   # small coupling for the rest of the lasers 
                                                                          # (value will remain for those not included in the problem)

        if indices is None:
            embedded[:N, :N] = coupling_matrix
        else:
            if len(indices) == 1:
                start = indices[0]
                embedded[start:start+N, start:start+N] = coupling_matrix
            else:
                indices = np.array(indices)
                embedded[np.ix_(indices, indices)] = coupling_matrix

        return embedded


# Function to analyze the solution from LPU and return binary state and its energy
def analyze_sol_XY(problem_matrix, phases_diffs):

    # This function recives the problem matrix and the phase difference solution and returns binary solution according to XY mapping
    phases = (np.cumsum(phases_diffs, axis=1)) % (2 * np.pi)
    N = phases.shape[1]

    # Initialize:
    energy = np.zeros(phases.shape[0])
    x = np.zeros(shape=phases.shape)
    correction = np.linspace(0, 0.1, N)                 # optional error sizes
    correction = np.append(correction, -1*correction)   # error may go both ways

    for i in range(phases.shape[0]) :
        
        min_bin_state, eng_new = best_energy_search_xy(np.exp(1J * phases[i, :]), np.real(problem_matrix))

        energies = [np.Inf]

        for corr in correction:
            correction_array = corr * np.arange(phases[i, :].shape[0])
            new_state = phases[i, :] + correction_array
            sol_new =(new_state[:])
            laser_sol_new, eng_new = best_energy_search_xy(np.exp(1J * sol_new), np.real(problem_matrix))
            if eng_new < np.min(energies):
                min_bin_state = laser_sol_new
            energies.append(eng_new)

        corrected = np.argmin(energies)
        x[i, :] = min_bin_state
        energy[i] = np.min(energies)

    min_ind = np.argmin(energy)

    return np.min(energy), x[min_ind,:]


import plotly.graph_objects as go
import plotly.express as px

def generateAnimation(outWave, save=False):

    # Number of frames in the animation
    num_frames = outWave.shape[0]
    color_scale = px.colors.qualitative.Set1[:outWave.shape[1]]

    fig = go.Figure()

    # Create text for the polar plot
    N = outWave.shape[1]
    text = [str(int(a)) for a in np.linspace(1, N, num=N, endpoint=True)]

    # Create data for the initial frame
    theta = np.angle(outWave[0, :]) *  180 / np.pi
    radius = np.abs(outWave[0, :])
    initial_frame_data = [go.Scatterpolar(r=radius, theta=theta, mode='markers+text', marker=dict(size=10, color=color_scale), text=text, textposition='top center', showlegend=False), 
                          ] 

    # Create the layout
    layout = go.Layout(
        showlegend=False,
        polar=dict(radialaxis=dict(visible=True)),
    )

    # Create the figure with the initial frame
    fig.add_trace(initial_frame_data[0])                      # Add the initial trace
    fig.update_layout(layout)            
    fig.update_xaxes(title_text="iteration")
    fig.update_layout(showlegend=True)

    # Define animation frames
    animation_frames = []

    for i in range(1, num_frames):
        theta = np.angle(outWave[i, :]) *  180 / np.pi
        r_values = np.abs(outWave[i, :])
        frame_data = [go.Scatterpolar(r=r_values, theta=theta, mode='markers+text', marker=dict(size=10, color=color_scale), name='polar plot', text=text, textposition='top center', showlegend=False),
                      ]
        animation_frames.append(go.Frame(data=frame_data, name=f"frame_{i}"))
    
    # Add frames to the figure
    fig.frames = animation_frames 

    # Define animation options
    animation_opts = dict(
        frame=dict(duration=500, redraw=True),
        fromcurrent=True
    )

    # Add play button
    fig.update_layout(
        updatemenus=[
            {
                'buttons': [
                    {
                        'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
                        'label': 'Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                        'label': 'Pause',
                        'method': 'animate'
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0.2,
                'yanchor': 'top'
            }
        ],
        template= "seaborn" # "plotly_dark"
    )

    # Define slider steps
    steps = []
    for i in range(num_frames):
        step = dict(
            method="animate",
            args=[
                [f"frame_{i}"],
                dict(
                    mode="immediate",
                    frame=dict(duration=300, redraw=True),
                    transition=dict(duration=0)
                ),
            ],
            label=str(i)
        )
        steps.append(step)

    # Add slider to layout
    fig.update_layout(
        sliders=[dict(
            active=0,
            currentvalue={"prefix": "Frame: "},
            pad={"t": 50},
            steps=steps
        )]
    )

    fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True)
            ),
            xaxis=dict(domain=[0.65, 1]),
            yaxis=dict(domain=[0.65, 1]),
            yaxis2=dict(domain=[0, 0.35], anchor='x', overlaying='y', side='right')
        )

    fig.update_layout(
            autosize=False,
            width=1200,
            height=800,
        )
    # Display & save the figure
    fig.show()
    # Save the figure as an HTML file
    if save:
        fig.write_html('polar_animation.html')
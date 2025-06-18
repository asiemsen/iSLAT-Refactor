#new entry point for iSLAT

# RUN WITH :
# cd iSLAT-Refactor
# python -m iSLAT-Refactor.main

import os
import numpy as np
import tkinter as tk
from tkinter import filedialog
import matplotlib 
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


from iSLAT.iSLAT_Refactor.mixed.mixed import selectfileinit
from iSLAT.iSLAT_Refactor.core.core import read_from_user_csv
from iSLAT.ir_model.moldata import MolData
import iSLAT.iSLAT_Refactor.globals 

# light mode settings
mode = False 
background = 'white'
foreground = 'black'

root = tk.Tk ()
root.withdraw ()
root.call ('wm', 'attributes', '.', '-topmost', True)

selectfileinit()

print (' ')
print ('Loading molecule files: ...')

molecules_data = read_from_user_csv()

for mol_name, mol_filepath, mol_label in molecules_data:
    # Import line lists from the ir_model folder
    mol_data = MolData(mol_name, mol_filepath)

    # Get the initial parameters for the current molecule, use default if not defined
    params = globals.INITIAL_PARAMETERS.get(mol_name, globals.DEFAULT_INITIAL_PARAMS)
    scale_exponent = params["scale_exponent"]
    scale_number = params["scale_number"]
    t_kin = params["t_kin"]
    radius_init = params["radius_init"]

    # Calculate and set n_mol_init for the current molecule
    n_mol_init = float (scale_number * (10 ** scale_exponent))

    # Use exec() to create the variables with specific variable names for each molecule
    exec (f"mol_{mol_name.lower ()} = MolData('{mol_name}', '{mol_filepath}')", globals ())
    exec (f"scale_exponent_{mol_name.lower ()} = {scale_exponent}", globals ())
    exec (f"scale_number_{mol_name.lower ()} = {scale_number}", globals ())
    exec (f"n_mol_{mol_name.lower ()}_init = {n_mol_init}", globals ())
    exec (f"t_kin_{mol_name.lower ()} = {t_kin}", globals ())
    exec (f"{mol_name.lower ()}_radius_init = {radius_init}", globals ())

    # Print the results (you can modify this part as needed)
    print (f"Molecule Initialized: {mol_name}")
    # print(f"scale_exponent_{mol_name.lower()} = {scale_exponent}")
    # print(f"scale_number_{mol_name.lower()} = {scale_number}")
    # print(f"n_mol_{mol_name.lower()}_init = {n_mol_init}")
    # print(f"t_kin_{mol_name.lower()} = {t_kin}")
    # print(f"{mol_name.lower()}_radius_init = {radius_init}")
    # print()  # Empty line for spacing

    # Store the initial values in the dictionary
    globals.initial_values[mol_name.lower ()] = {
        "scale_exponent": scale_exponent,
        "scale_number": scale_number,
        "t_kin": t_kin,
        "radius_init": radius_init,
        "n_mol_init": n_mol_init
    }

# Creating the graph
fig = plt.figure(figsize=(15, 8.5))
# fig = plt.figure()
gs = GridSpec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1, 1.5])
ax1 = fig.add_subplot (gs[0, :])
ax2 = fig.add_subplot (gs[1, 0])
ax3 = fig.add_subplot (gs[1, 1])

ax2.set_xlabel('Wavelength (μm)')
ax1.set_ylabel('Flux density (Jy)')
ax2.set_ylabel('Flux density (Jy)')
ax1.set_xlim(xmin=globals.xp1, xmax=globals.xp2) # (xmin = xp1, xmax = xp2)
plt.rcParams['font.size'] = 10

#DUMMY DATA 
dummy_wave = np.linspace(0, 10, 10)    # 10 points from 0 to 1 on x-axis
dummy_flux = np.zeros_like(dummy_wave)

data_line, = ax1.plot(globals.wave_data, globals.flux_data, color=foreground, linewidth=1)

data_line.set_label ('Data')
sum_line, = ax1.plot ([], [], color='purple', linewidth=1)
sum_line.set_label ('Sum')
ax1.legend ()

ax2.set_frame_on (False)
ax3.set_frame_on (False)

# make empty lines for the second plot
ax2.set_title ('Line inspection plot', fontsize='medium')
data_line_select, = ax2.plot ([], [], color=foreground, linewidth=1)








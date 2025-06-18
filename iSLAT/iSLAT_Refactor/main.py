#new entry point for iSLAT

# RUN WITH :
# cd iSLAT-Refactor
# python -m iSLAT-Refactor.main


import tkinter as tk

from mixed.mixed import selectfileinit
from core.core import read_from_user_csv
from ir_model.moldata import MolData
from globals import INITIAL_PARAMETERS, DEFAULT_INITIAL_PARAMS, initial_values

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
    params = INITIAL_PARAMETERS.get(mol_name, DEFAULT_INITIAL_PARAMS)
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
    initial_values[mol_name.lower ()] = {
        "scale_exponent": scale_exponent,
        "scale_number": scale_number,
        "t_kin": t_kin,
        "radius_init": radius_init,
        "n_mol_init": n_mol_init
    }




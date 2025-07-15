#new entry point for iSLAT

# RUN WITH :
# cd iSLAT
# python -m iSLAT-Refactor.main

iSLAT_version = "Refactor Build"
import matplotlib 
matplotlib.use('TkAgg') # Use TkAgg backend
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
import matplotlib 
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_tkagg import(FigureCanvasTkAgg, NavigationToolbar2Tk)

from iSLAT_Refactor.mixed.select_file import selectfileinit
from iSLAT_Refactor.core.read_csv import read_from_user_csv
from ir_model.moldata import MolData
from iSLAT_Refactor import app_globals
from iSLAT_Refactor.GUI.tooltip import ToolTip, CreateToolTip
from iSLAT_Refactor.core.molecule_manager import MoleculeManager
from iSLAT_Refactor.GUI.gui_manager import GUI_Manager
from iSLAT_Refactor.core.app_controller import AppController

print("LOADING REFACTORED iSLAT")

# light mode settings
mode = False 
background = 'white'
foreground = 'black'

window = tk.Tk()

window.withdraw()
window.call('wm', 'attributes', '.', '-topmost', True)
window.protocol("WM_DELETE_WINDOW", window.quit)


selectfileinit()

print(' ')
print('Loading molecule files: ...')

molecules_data = read_from_user_csv()

print(app_globals.file_name)

moleculeManager = MoleculeManager(molecules_data)
guiManager = GUI_Manager(window, moleculeManager)

appController = AppController(moleculeManager, guiManager)


plt.interactive(False)



# for row, (mol_name, _, _) in enumerate(molecules_data, start=1):
#     # Get the molecule name in lower case
#     mol_name_lower = mol_name.lower()

#     # Get the line object
#     line_var = globals().get(f"{mol_name_lower}_line")
#     # Chdeseck if the line object exists and has a color attribute
#     if line_var and hasattr(line_var, 'get_color'):
#         # Get the color of the line
#         line_color = line_var.get_color()

#         # Get the color button from the grid_slaves listatomi
#         color_button = molecule_frame.grid_slaves(row=row, column=6)[0]

#         # Set the background color of the color button
#         color_button.configure(bg=line_color)
#     else:
#         print('Line object or color attribute not found for:', mol_name)

moleculeManager.createLines(molecules_data, guiManager.ax1)

# This must happen after createLines
guiManager.molecules_frame.configureButton(appController)
moleculeManager.calcSum(guiManager.ax1, guiManager.canvas)



# window.attributes('-fullscreen', True)   # full monitor
# window.state('zoomed') 
# window.update()
# window.deiconify()

window.mainloop()


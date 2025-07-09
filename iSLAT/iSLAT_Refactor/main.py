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

moleculeManager = MoleculeManager(molecules_data)

guiManager = GUI_Manager(window, moleculeManager)



# # create buttons for top of GUI
# nb_of_columns = 10  # to be replaced by the relevant number
# title_frame = tk.Frame(window)
# title_frame.grid(row=0, column=0, columnspan=nb_of_columns, sticky='ew')

# # Create a frame to hold the canvasscroll and both scrollbars
# outer_frame = tk.Frame(window)
# outer_frame.grid(row=title_frame.grid_info()['row'] + title_frame.grid_info()['rowspan'], column=0, rowspan=10,
#                   columnspan=5, sticky="nsew")

# # Create a canvasscroll widget
# canvasscroll = tk.Canvas(outer_frame)
# canvasscroll.grid(row=0, column=0, sticky="nsew")

# # Create vertical and horizontal scrollbar widgets and associate them with the canvasscroll
# vscrollbar = tk.Scrollbar(outer_frame, orient="vertical", command=canvasscroll.yview)
# vscrollbar.grid(row=0, column=1, sticky="ns")
# hscrollbar = tk.Scrollbar(outer_frame, orient="horizontal", command=canvasscroll.xview)
# hscrollbar.grid(row=1, column=0, columnspan= 2, sticky="ew")

# # Configure the canvasscroll to use the scrollbars
# canvasscroll.configure(yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)

# # Allow resizing of the canvasscroll and outer_frame
# outer_frame.grid_rowconfigure(0, weight=1)
# outer_frame.grid_columnconfigure(0, weight=1)

# # Create the frame that will contain your actual content
# molecule_frame = tk.Frame(canvasscroll, borderwidth=2)  # , relief="groove")
# canvasscroll.create_window((0, 0), window=molecule_frame, anchor="nw")

# # Configure the canvasscroll scroll region
# def on_frame_configure(event):
#     canvasscroll.configure(scrollregion=canvasscroll.bbox("all"))

# molecule_frame.bind("<Configure>", on_frame_configure)

# # Create the frame with the specified properties
# # molecule_frame = tk.Frame(window, borderwidth=2, relief="groove")
# # molecule_frame.grid(row=1, column=0, rowspan=10, columnspan=5, sticky="nsew")

# # Create labels for columns
# for col, label in enumerate(column_labels):
#     label_widget = tk.Label(molecule_frame, text=label)
#     label_widget.grid(row=0, column=col)

# Loop to create rows of input fields and buttons for each chemical
# nextrow = 1  # Start with row 1
# for row, (mol_name, mol_filepath, mol_label) in enumerate(molecules_data):
#     # global nextrow
#     y_row = start_y + row_height * (num_rows - row - 1)
#     row = row + 1
#     # Get the initial values for the current chemical from the dictionary
#     # params = app_globals.initial_values[mol_name.lower()]
#     params = moleculeManager.moleculeDictionary[mol_name.lower()]
#     scale_exponent = params["scale_exponent"]
#     scale_number = params["scale_number"]
#     t_kin = params["t_kin"]
#     radius_init = params["radius"]
#     n_mol_init = params["n_mol"]

#     # Row label
#     exec(f"{mol_name.lower()}_rowl_field = tk.Entry(molecule_frame, width=6)")
#     eval(f"{mol_name.lower()}_rowl_field").grid(row=row, column=0)
#     eval(f"{mol_name.lower()}_rowl_field").insert(0, f"{mol_name}")

#     # Temperature input field
#     exec(f"{mol_name.lower()}_temp_field = tk.Entry(molecule_frame, width=4)")
#     eval(f"{mol_name.lower()}_temp_field").grid(row=row, column=1)
#     eval(f"{mol_name.lower()}_temp_field").insert(0, f"{t_kin}")
#     # eval(f"{mol_name.lower()}_temp_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
#     #     f"{mol_name.lower()}_temp_field"]: submit_temp(ce.get(), mn))

#     CreateToolTip(eval(f"{mol_name.lower()}_temp_field"), text='Excitation temperature\n'
#                                                                   'units: K')

#     # Radius input field
#     exec(f"{mol_name.lower()}_rad_field = tk.Entry(molecule_frame, width=4)")
#     eval(f"{mol_name.lower()}_rad_field").grid(row=row, column=2)
#     eval(f"{mol_name.lower()}_rad_field").insert(0, f"{radius_init}")
#     # eval(f"{mol_name.lower()}_rad_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
#     #     f"{mol_name.lower()}_rad_field"]: submit_rad(ce.get(), mn))

#     CreateToolTip(eval(f"{mol_name.lower()}_rad_field"), text='Equivalent radius\n'
#                                                                  'units: au')

#     # Column Density input field
#     exec(f"{mol_name.lower()}_dens_field = tk.Entry(molecule_frame, width=6)")
#     eval(f"{mol_name.lower()}_dens_field").grid(row=row, column=3)
#     eval(f"{mol_name.lower()}_dens_field").insert(0, f"{n_mol_init:.{1}e}")
#     # eval(f"{mol_name.lower()}_dens_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
#     #     f"{mol_name.lower()}_dens_field"]: submit_col(ce.get(), mn))

#     CreateToolTip(eval(f"{mol_name.lower()}_dens_field"), text='Column density\n'
#                                                                   'units: cm^(-2)')

#     # Visibility Checkbutton
#     if mol_name.lower() == 'h2o':
#         exec(f"{mol_name.lower()}_vis_status = tk.BooleanVar()")
#         exec(f"{mol_name.lower()}_vis_status.set(True)")  # Set the initial state
#         exec(
#             f"{mol_name.lower()}_vis_checkbutton = tk.Checkbutton(molecule_frame, text='', variable={mol_name.lower()}_vis_status, onvalue=True, offvalue=False, command=lambda mn=mol_name.lower(): moleculeManager.toggle_visible(mn))")
#         exec(f"{mol_name.lower()}_vis_checkbutton.select()")
#     else:
#         globals()[f"{mol_name.lower()}_vis_status"] = tk.BooleanVar()
#         exec(
#             f"{mol_name.lower()}_vis_checkbutton = tk.Checkbutton(molecule_frame, text='', variable={mol_name.lower()}_vis_status, onvalue=True, offvalue=False, command=lambda mn=mol_name.lower(): moleculeManager.toggle_visible(mn))")
#         globals()[f"{mol_name.lower()}_vis_status"].set(False)  # Set the initial state


#     eval(f"{mol_name.lower()}_vis_checkbutton").grid(row=row, column=4)

#     CreateToolTip(eval(f"{mol_name.lower()}_vis_checkbutton"), text='Turn on/off this\n'
#                                                                        'model in the plot')

#     # Delete button
#     del_button = tk.Button(molecule_frame, text="X")
#     #                         command=lambda widget=eval(f"{mol_name.lower()}_rowl_field"): delete_row(widget))
#     # del_button.grid(row=row, column=5)

#     CreateToolTip(del_button, text='Remove this model\n'
#                                     'from the GUI')

#     color_button = tk.Button(molecule_frame, text=" ")
#     #                           command=lambda widget=eval(f"{mol_name.lower()}_rowl_field"): choose_color(widget))
#     # color_button.grid(row=row, column=6)

#     CreateToolTip(color_button, text='Change color\n'
#                                       'for this model')

#     nextrow = row + 1



# files_frame = tk.Frame(window, borderwidth=2, relief="groove", bg='gray')
# files_frame.grid(row=outer_frame.grid_info()['row'] + outer_frame.grid_info()['rowspan'], column=0, rowspan=7,
#                   columnspan=5, sticky="nsew")


# # Configure columns to expand and fill the width
# for i in range(5):
#     files_frame.columnconfigure(i, weight=1)

# # Create a frame to hold the box outline
# box_frame = tk.Frame(files_frame)
# box_frame.grid(row=1, column=0, columnspan=5, sticky='nsew')

# specfile_label = tk.Label(files_frame, text='Spectrum Data File:')
# specfile_label.grid(row=0, column=0, columnspan=5, sticky='nsew')  # Center-align using grid

# linefile_label = tk.Label(files_frame, text='Input Line List:')
# linefile_label.grid(row=2, column=0, columnspan=5, sticky='nsew')  # Center-align using grid

# linefile_label = tk.Label(files_frame, text='Output Line Measurements:')
# linefile_label.grid(row=4, column=0, columnspan=5, sticky='nsew')  # Center-align using grid

# # Create a frame to hold the box outline
# linebox_frame = tk.Frame(files_frame)
# linebox_frame.grid(row=3, column=0, columnspan=5, sticky='nsew')

# # Create a label widget inside the frame to create the box outline
# linebox_label = tk.Label(linebox_frame, text='', relief='solid', borderwidth=1,
#                           height=2)  # Adjust the height value as needed
# linebox_label.pack(side="top", fill="both", expand=True)

# # Create a label inside the box_frame and center-align it
# linefile_name_label = tk.Label(linebox_label, text='')
# linefile_name_label.grid(row=0, column=0, sticky='nsew')  # Center-align using grid

# # Create a frame to hold the box outline
# savelinebox_frame = tk.Frame(files_frame)
# savelinebox_frame.grid(row=5, column=0, columnspan=5, sticky='nsew', pady=(0, 10))

# # Create a label widget inside the frame to create the box outline
# linesavebox_label = tk.Label(savelinebox_frame, text='', relief='solid', borderwidth=1,
#                               height=2)  # Adjust the height value as needed
# linesavebox_label.pack(side="top", fill="both", expand=True)

# # Create a label inside the box_frame and center-align it
# savelinefile_name_label = tk.Label(linesavebox_label, text='')
# savelinefile_name_label.grid(row=0, column=0, sticky='nsew')  # Center-align using grid

# # Create a label widget inside the frame to create the box outline
# box_label = tk.Label(box_frame, text='', relief='solid', borderwidth=1, height=2)  # Adjust the height value as needed
# box_label.pack(fill=tk.BOTH, expand=True)

# # Create a label inside the box_frame and center-align it
# file_name_label = tk.Label(box_label, text=str(app_globals.file_name))
# file_name_label.grid(row=0, column=0, sticky='nsew')  # Center-align using grid

# file_button = tk.Button(files_frame, text='Open File') #, command=selectfile
# file_button.grid(row=1, column=5)

# linefile_button = tk.Button(files_frame, text='Open File') #, command=selectlinefile
# linefile_button.grid(row=3, column=5)

# linesave_button = tk.Button(files_frame, text='Define File')# , command=savelinefile
# linesave_button.grid(row=5, column=5, pady=(0, 10))

# # Add some space below files_frame
# # tk.Label(files_frame, text="").grid(row=4, column=0)

# plotparams_frame = tk.Frame(window, borderwidth=2, relief="groove")
# plotparams_frame.grid(row=files_frame.grid_info()['row'] + files_frame.grid_info()['rowspan'], column=0, rowspan=6,
#                        columnspan=5, sticky="nsew")

# # Create and place the xp1 text box in row 12, column 0
# xp1_label = tk.Label(plotparams_frame, text="Plot start:")
# xp1_label.grid(row=0, column=0)
# xp1_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
# xp1_entry.insert(0, str(app_globals.xp1))
# xp1_entry.grid(row=0, column=1)
# # xp1_entry.bind("<Return>", lambda event: update_xp1_rng())

# # Create and place the rng text box in row 12, column 2
# rng_label = tk.Label(plotparams_frame, text="Plot range:")
# rng_label.grid(row=0, column=2)
# rng_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
# rng_entry.insert(0, str(app_globals.rng))
# rng_entry.grid(row=0, column=3)
# # rng_entry.bind("<Return>", lambda event: update_xp1_rng())

# # Create and place the min_lamb text box in row 2, column 0
# min_lamb_label = tk.Label(plotparams_frame, text="Min. Wave:")
# min_lamb_label.grid(row=1, column=0)
# min_lamb_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
# min_lamb_entry.insert(0, str(app_globals.min_lamb))
# min_lamb_entry.grid(row=1, column=1)
# # min_lamb_entry.bind("<Return>", lambda event: update_initvals())

# # Create and place the max_lamb text box in row 2, column 2
# max_lamb_label = tk.Label(plotparams_frame, text="Max. Wave:")
# max_lamb_label.grid(row=1, column=2)
# max_lamb_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
# max_lamb_entry.insert(0, str(app_globals.max_lamb))
# max_lamb_entry.grid(row=1, column=3)
# # max_lamb_entry.bind("<Return>", lambda event: update_initvals())

# # Create and place the dist text box in row 3, column 0
# dist_label = tk.Label(plotparams_frame, text="Distance:")
# dist_label.grid(row=2, column=0)
# dist_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
# dist_entry.insert(0, str(app_globals.dist))
# dist_entry.grid(row=2, column=1)
# # dist_entry.bind("<Return>", lambda event: update_initvals())

# # Create and place the RV text box in row 3, column 0
# dist_label = tk.Label(plotparams_frame, text="Stellar RV:")
# dist_label.grid(row=2, column=2)
# star_rv_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
# star_rv_entry.insert(0, str(app_globals.star_rv))
# star_rv_entry.grid(row=2, column=3)
# # star_rv_entry.bind("<Return>", lambda event: update_initvals())

# # Create and place the fwhm text box in row 3, column 2
# fwhm_label = tk.Label(plotparams_frame, text="FWHM:")
# fwhm_label.grid(row=3, column=0)
# fwhm_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
# fwhm_entry.insert(0, str(app_globals.fwhm))
# fwhm_entry.grid(row=3, column=1)
# # fwhm_entry.bind("<Return>", lambda event: update_initvals())

# # Create and place the fwhm text box in row 3, column 2
# intrinsic_line_width_label = tk.Label(plotparams_frame, text="Broadening:")
# intrinsic_line_width_label.grid(row=3, column=2)
# intrinsic_line_width_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
# intrinsic_line_width_entry.insert(0, str(app_globals.intrinsic_line_width))
# intrinsic_line_width_entry.grid(row=3, column=3)
# # intrinsic_line_width_entry.bind("<Return>", lambda event: update_initvals())

# # Create and place the xp1 text box in row 12, column 0
# specsep_label = tk.Label(plotparams_frame, text="Line Separ.:")
# #specsep_label.grid(row=4, column=2, pady=(0, 45))
# specsep_label.grid(row=4, column=2)
# specsep_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
# specsep_entry.insert(0, str(app_globals.specsep))
# #specsep_entry.grid(row=4, column=3, pady=(0, 45))
# specsep_entry.grid(row=4, column=3)


# # Create a dropdown menu in the new window
# spanselectlab = tk.Label(plotparams_frame, text="Molecule:")
# #spanselectlab.grid(row=4, column=0, pady=(0, 45))
# spanselectlab.grid(row=4, column=0)
# spanoptionsvar = [m[0] for m in molecules_data]  # + ["SUM"]
# spandropdowntext = tk.StringVar()
# spandropd = ttk.Combobox(plotparams_frame, textvariable=spandropdowntext, values=spanoptionsvar, width=6)
# spandropd.set(spanoptionsvar[0])
# #spandropd.grid(row=4, column=1, pady=(0, 45))
# spandropd.grid(row=4, column=1)

# # spandropd.bind("<<ComboboxSelected>>", lambda event: on_span_select((spanoptionsvar[spandropd.current()]).lower()))

# # Create a Tkinter button to import additional hitran molecules
# import_button = tk.Button(title_frame, text="HITRAN query", bg='lightgray', activebackground='gray') # , command=import_molecule
# import_button.grid(row=0, column=0)

# defmol_button = tk.Button(title_frame, text='Default Molecules', bg='lightgray', activebackground='gray') # , command=lambda: load_defaults_from_file(), width=12, height=1)
                           
# defmol_button.grid(row=0, column=1)

# # Create the 'Add Mol.' button
# addmol_button = tk.Button(title_frame, text='Add Molecule', bg='lightgray', activebackground='gray') # command=lambda: add_molecule_data(), width=12, height=1)
                           
# addmol_button.grid(row=0, column=2)

# # Create the 'Save Changes' button
# saveparams_button = tk.Button(title_frame, text='Save Parameters', bg='lightgray', activebackground='gray') #  command=lambda: saveparams_button_clicked(), width=12, height=1)
                              
# saveparams_button.grid(row=0, column=3)

# # Create the 'Load Save' button
# loadparams_button = tk.Button(title_frame, text='Load Parameters', bg='lightgray', activebackground='gray') # command=lambda: load_variables_from_file(file_name), width=12, height=1)
                               
# loadparams_button.grid(row=0, column=4)

# export_button = tk.Button(title_frame, text='Export Models', bg='lightgray',  width=12,
#                            height=1) # command=export_spectrum,
# export_button.grid(row=0, column=5)

# # Create a Tkinter button to toggle the legend
# toggle_button = tk.Button(title_frame, text="Toggle Legend", bg='lightgray', activebackground='gray',
#                             width=12) # command=toggle_legend,
# toggle_button.grid(row=0, column=6)

# # Create and place the buttons for other functions
# functions_frame = tk.Frame(window, borderwidth=2, relief="groove")
# functions_frame.grid(row=plotparams_frame.grid_info()['row'] + plotparams_frame.grid_info()['rowspan'], column=0,
#                       rowspan=6, columnspan=5, sticky='nsew')

# save_button = tk.Button(functions_frame, text="Save Line", bg='lightgray', activebackground='gray', # command=Save,
#                          width=13, height=1)
# save_button.grid(row=0, column=0)

# fit_button = tk.Button(functions_frame, text="Fit Line", bg='lightgray', activebackground='gray', # command=fit_onselect,
#                         width=13, height=1)
# fit_button.grid(row=0, column=1)

# savedline_button = tk.Button(functions_frame, text="Show Saved Lines", bg='lightgray', activebackground='gray') #  command=print_saved_lines, width=13, height=1)
                             
# savedline_button.grid(row=1, column=0)

# fitsavedline_button = tk.Button(functions_frame, text="Fit Saved Lines", bg='lightgray', activebackground='gray') # command=fit_saved_lines, width=13, height=1)
                                 
# fitsavedline_button.grid(row=1, column=1)

# autofind_button = tk.Button(functions_frame, text="Find Single Lines", bg='lightgray', activebackground='gray') # command=single_finder, width=13, height=1)
                             
# autofind_button.grid(row=2, column=0)

# # Create the 'Atomic lines' button
# atomlines_button = tk.Button(functions_frame, text='Show Atomic Lines', bg='lightgray', activebackground='gray') # command=lambda: print_atomic_lines(), width=13, height=1)
                              
# atomlines_button.grid(row=2, column=1)

# # Create the 'Slabfit' button
# slabfit_button = tk.Button(functions_frame, text='Single Slab Fit', bg='lightgray', activebackground='gray') # command=lambda: run_slabfit(), width=13, height=1)
                            
# slabfit_button.grid(row=3, column=0)

# # Create the 'De-blender' button
# deblender_button = tk.Button(functions_frame, text='Line De-blender', bg='lightgray', activebackground='gray') #  command=lambda: fitmulti_onselect(), width=13, height=1)
                           
# deblender_button.grid(row=3, column=1)

# # DELETE ----------------------
# # Create a frame for the Text widget
# text_frame = tk.Frame(window)
# text_frame.grid(row=functions_frame.grid_info()['row'] + functions_frame.grid_info()['rowspan'], column=0,
#                  columnspan=5, sticky='nsew')

# # Create a Text widget within the frame
# data_field = tk.Text(text_frame, wrap="word", height=13, width=24)
# data_field.pack(fill="both", expand=True)

# # Storing the callback for on_xlims_change()
# # ax1.callbacks.connect('xlim_changed', on_xlims_change)



# # Create a FigureCanvasTkAgg widget to embed the figure in the tkinter window
# canvas = FigureCanvasTkAgg(fig, master=window)
# canvas_widget = canvas.get_tk_widget()

# # Place the canvas widget in column 9, row 1
# canvas_widget.grid(row=1, column=5, rowspan=100, sticky='nsew')

# # Allow column 9 and row 1 to expandc
# window.grid_columnconfigure(5, weight=1)
# window.grid_rowconfigure(100, weight=1)

# # Create a frame for the toolbar inside the title_frame
# toolbar_frame = tk.Frame(title_frame)
# toolbar_frame.grid(row=0, column=9, columnspan=2, sticky="nsew")  # Place the frame in row 0, column 9
# # Create a toolbar and update it
# toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
# toolbar.update()

# title_frame.grid_columnconfigure(9, weight=1)

plt.interactive(False)

# file_button = tk.Button(files_frame, text='Open File', ) # command=selectfile
# file_button.grid(row=1, column=5)

# linefile_button = tk.Button(files_frame, text='Open File', ) # command=selectlinefile
# linefile_button.grid(row=3, column=5)

# linesave_button = tk.Button(files_frame, text='Define File', ) # command=savelinefile
# linesave_button.grid(row=5, column=5, pady=(0, 10))



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



# window.attributes('-fullscreen', True)   # full monitor
# window.state('zoomed') 
# window.update()
# window.deiconify()

window.mainloop()


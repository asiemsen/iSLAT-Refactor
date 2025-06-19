from tkinter import filedialog
import tkinter as tk
import os
import numpy as np
import pandas as pd

from iSLAT_Refactor import app_globals

def selectfileinit():

    spectra_directory = os.path.abspath("../EXAMPLE-data")
    filetypes = [('CSV Files', '*.csv')]
    # Ask the user to select a file
    infiles = filedialog.askopenfilename(multiple=True, title='Choose Spectrum Data File', filetypes=filetypes,
                                         initialdir=spectra_directory)

    if infiles:
        for app_globals.file_path in infiles:
            # Process each selected file
            print(' ')
            print("Selected file:", app_globals.file_path)
            app_globals.file_name = os.path.basename(app_globals.file_path)
            # code to process each file
            app_globals.input_spectrum_data = pd.read_csv(filepath_or_buffer=app_globals.file_path, sep=',')
            app_globals.wave_data = np.array(app_globals.input_spectrum_data['wave'])
            app_globals.wave_original = np.array(app_globals.input_spectrum_data['wave'])
            app_globals.flux_data = np.array(app_globals.input_spectrum_data['flux'])
            if 'err' in app_globals.input_spectrum_data:
                app_globals.err_data = np.array(app_globals.input_spectrum_data['err'])
            else:
                app_globals.err_data = np.full_like(app_globals.flux_data, np.nanmedian(app_globals.flux_data) / 100)  # assumed, if not present

                # Set initial values of xp1 and rng
            fig_max_limit = np.nanmax(app_globals.wave_data)
            fig_min_limit = np.nanmin(app_globals.wave_data)
            app_globals.xp1 = np.around(fig_min_limit + (fig_max_limit - fig_min_limit) / 2, decimals=2)
            app_globals.rng = np.around((fig_max_limit - fig_min_limit) / 10, decimals=2)
            app_globals.xp2 = app_globals.xp1 + app_globals.rng

            # now = dt.now()
            # dateandtime = now.strftime("%d-%m-%Y-%H-%M-%S")
            # print(dateandtime)
            # svd_line_file = f'savedlines-{dateandtime}.csv'

        # Ask the user to select the mode (light or dark)
        mode_dialog = tk.messagebox.askquestion("Select Mode", "Would you like to start iSLAT in Dark Mode?")

        if mode_dialog == 'yes':
            app_globals.mode= True  # Dark mode
        else:
            app_globals.mode= False  # Light mode
    else:
        print("No files selected.")
from tkinter import filedialog
import tkinter as tk
import os
import numpy as np
import pandas as pd

def selectfileinit():
    global file_path
    global file_name
    global wave_data, flux_data, err_data, wave_original
    global input_spectrum_data
    global filename_box_data
    global mode
    global xp1, rng, xp2

    spectra_directory = os.path.abspath("../EXAMPLE-data")
    filetypes = [('CSV Files', '*.csv')]
    # Ask the user to select a file
    infiles = filedialog.askopenfilename(multiple=True, title='Choose Spectrum Data File', filetypes=filetypes,
                                         initialdir=spectra_directory)

    if infiles:
        for file_path in infiles:
            # Process each selected file
            print(' ')
            print("Selected file:", file_path)
            file_name = os.path.basename(file_path)
            # code to process each file
            input_spectrum_data = pd.read_csv(filepath_or_buffer=file_path, sep=',')
            wave_data = np.array(input_spectrum_data['wave'])
            wave_original = np.array(input_spectrum_data['wave'])
            flux_data = np.array(input_spectrum_data['flux'])
            if 'err' in input_spectrum_data:
                err_data = np.array(input_spectrum_data['err'])
            else:
                err_data = np.full_like(flux_data, np.nanmedian(flux_data) / 100)  # assumed, if not present

                # Set initial values of xp1 and rng
            fig_max_limit = np.nanmax(wave_data)
            fig_min_limit = np.nanmin(wave_data)
            xp1 = np.around(fig_min_limit + (fig_max_limit - fig_min_limit) / 2, decimals=2)
            rng = np.around((fig_max_limit - fig_min_limit) / 10, decimals=2)
            xp2 = xp1 + rng

            # now = dt.now()
            # dateandtime = now.strftime("%d-%m-%Y-%H-%M-%S")
            # print(dateandtime)
            # svd_line_file = f'savedlines-{dateandtime}.csv'

        # Ask the user to select the mode (light or dark)
        mode_dialog = tk.messagebox.askquestion("Select Mode", "Would you like to start iSLAT in Dark Mode?")

        if mode_dialog == 'yes':
            mode = True  # Dark mode
        else:
            mode = False  # Light mode
    else:
        print("No files selected.")
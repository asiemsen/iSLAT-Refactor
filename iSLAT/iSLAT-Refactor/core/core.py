# -----------------------------------------------------------------------------
# create HITRAN folder, only needed for first start
# -----------------------------------------------------------------------------

HITRAN_folder = "HITRANdata"
os.makedirs(HITRAN_folder, exist_ok=True)


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    mols = ["H2", "HD", "H2O", "H218O", "CO2", "13CO2", "CO", "13CO", "C18O", "CH4", "HCN", "H13CN", "NH3", "OH",
            "C2H2", "13CCH2", "C2H4", "C4H2", "C2H6", "HC3N"]
    basem = ["H2", "H2", "H2O", "H2O", "CO2", "CO2", "CO", "CO", "CO", "CH4", "HCN", "HCN", "NH3", "OH", "C2H2", "C2H2",
             "C2H4", "C4H2", "C2H6", "HC3N"]
    isot = [1, 2, 1, 2, 1, 2, 1, 2, 3, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1]

    min_wave = 0.3  # micron
    max_wave = 1000  # micron

    min_vu = 1 / (min_wave / 1E6) / 100.
    max_vu = 1 / (max_wave / 1E6) / 100.

    print(' ')
    print('Checking for HITRAN files: ...')

    for mol, bm, iso in zip(mols, basem, isot):
        save_folder = 'HITRANdata'
        file_path = os.path.join(save_folder, "data_Hitran_2020_{:}.par".format(mol))

        if os.path.exists(file_path):
            print("File already exists for mol: {:}. Skipping.".format(mol))
            continue

        print("Downloading data for mol: {:}".format(mol))
        Htbl, qdata, M, G = get_Hitran_data(bm, iso, min_vu, max_vu)

        with open(file_path, 'w') as fh:
            fh.write("# HITRAN 2020 {:}; id:{:}; iso:{:};gid:{:}\n".format(mol, M, iso, G))
            fh.write("# Downloaded from the Hitran website\n")
            fh.write("# {:s}\n".format(str(datetime.date.today())))
            fh = write_partition_function(fh, qdata)
            fh = write_line_data(fh, Htbl)

        print("Data for Mol: {:} downloaded and saved.".format(mol))


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

# Define the default molecules and their file path; the folder must be in the same path as iSLAT
molecules_data = [
    ("H2O", "HITRANdata/data_Hitran_2020_H2O.par", "H$_2$O"),
    ("OH", "HITRANdata/data_Hitran_2020_OH.par", "OH"),
    ("HCN", "HITRANdata/data_Hitran_2020_HCN.par", "HCN"),
    ("C2H2", "HITRANdata/data_Hitran_2020_C2H2.par", "C$_2$H$_2$"),
    ("CO2", "HITRANdata/data_Hitran_2020_CO2.par", "CO$_2$"),
    ("CO", "HITRANdata/data_Hitran_2020_CO.par", "CO")
    # Add more molecules here if needed
]

default_data = [
    ("H2O", "HITRANdata/data_Hitran_2020_H2O.par", "H$_2$O"),
    ("OH", "HITRANdata/data_Hitran_2020_OH.par", "OH"),
    ("HCN", "HITRANdata/data_Hitran_2020_HCN.par", "HCN"),
    ("C2H2", "HITRANdata/data_Hitran_2020_C2H2.par", "C$_2$H$_2$"),
    ("CO2", "HITRANdata/data_Hitran_2020_CO2.par", "CO$_2$"),
    ("CO", "HITRANdata/data_Hitran_2020_CO.par", "CO")
]

molecules_data_default = molecules_data.copy()

deleted_molecules = []

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

# Create necessary folders, if it doesn't exist (typically at first launch of iSLAT)
save_folder = "SAVES"
os.makedirs(save_folder, exist_ok=True)
output_dir = "../MODELS"
os.makedirs(output_dir, exist_ok=True)
linesave_folder = "LINESAVES"
os.makedirs(linesave_folder, exist_ok=True)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

# read more molecules if saved by the user in a previous iSLAT session
def read_from_csv():
    global file_name
    filename = os.path.join(save_folder, f"{file_name}-molsave.csv")

    if os.path.exists(filename):
        try:
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header row
                return [tuple(row[:3]) for row in reader]
        except FileNotFoundError:
            pass
    return molecules_data

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def read_default_csv():
    global file_name
    filename = os.path.join(save_folder, f"default.csv")

    if os.path.exists(filename):
        try:
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header row
                return [tuple(row[:3]) for row in reader]
        except FileNotFoundError:
            pass
    return molecules_data

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------


# read more molecules if saved by the user in a previous iSLAT session
def read_from_user_csv():
    global file_name
    filename = os.path.join(save_folder, f"molecules_list.csv")

    if os.path.exists(filename):
        try:
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header row
                return [tuple(row[:3]) for row in reader]
        except FileNotFoundError:
            pass
    return molecules_data

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

# Set default initial parameters for a new molecule
default_initial_params = {
    "scale_exponent": 17,
    "scale_number": 1,
    "t_kin": 600,
    "radius_init": 0.5
}

# Define the initial parameters for default molecules
initial_parameters = {
    "H2O": {
        "scale_exponent": 18,
        "scale_number": 1,
        "t_kin": 850,
        "radius_init": 0.5
    },
    "OH": {
        "scale_exponent": 16,
        "scale_number": 1,
        "t_kin": 2000,
        "radius_init": 0.3
    },
    "HCN": {
        "scale_exponent": 16,
        "scale_number": 1,
        "t_kin": 850,
        "radius_init": 0.5
    },
    "C2H2": {
        "scale_exponent": 17,
        "scale_number": 1,
        "t_kin": 600,
        "radius_init": 0.1
    },
    "CO2": {
        "scale_exponent": 17,
        "scale_number": 1,
        "t_kin": 300,
        "radius_init": 0.5
    },
    "CO": {
        "scale_exponent": 18,
        "scale_number": 1,
        "t_kin": 1200,
        "radius_init": 0.4
    }
}

# Set-up default input parameters for model generation
min_lamb = 4.5
max_lamb = 28.
dist = 160.0
star_rv = 0.0
fwhm = 130.  # FWHM of the observed lines or instrument
pix_per_fwhm = 10  # number of pixels per fwhm element

intrinsic_line_width = 1.0
cc = 2.99792458e5  # speed of light in km/s
model_line_width = cc / fwhm
model_pixel_res = (np.mean([min_lamb, max_lamb]) / cc * fwhm) / pix_per_fwhm

# Constants used in generating the rotation diagram
au = 1.496e11  # 1AU in m
pc = 3.08567758128e18  # From parsec to cm
ccum = 2.99792458e14  # speed of light in um/s
hh = 6.62606896e-27  # erg s

# Dictionary to store the initial values for each chemical
initial_values = {}

# define other defaults needed below
spanmol = "h2o"
specsep = .01  # default value for the separation to determine if line is single
fwhmtolerance = 5  # default value for the tolerance in FWHM for the de-blender (in km/s)
centrtolerance = 0.0001  # default value for the tolerance in centroid for the de-blender (in um)
line_threshold = 0.03  # percent value (where 0.01 = 1%) of the strongest line in the plot;
# lines below this this limit are ignored in the plot and in the single line selection

# -----------------------------------------------------------------------------
# NEEDS TO BE REFACTORED, HAS SOME GUI COMPONENTS
# -----------------------------------------------------------------------------

def run_slabfit():
    global spanmol

    try:
        linelistpath
    except NameError:
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'Input line measurement file is not defined!')
    else:

        # Update the main GUI data_field
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'Fitting slab for molecule: ' + spanmol)

        save_folder = 'MODELS'
        mol = spanmol
        mol_path = next(mol_data[1] for mol_data in molecules_data if mol_data[0] == spanmol.upper())

        min_lamb = float(min_lamb_entry.get())
        max_lamb = float(max_lamb_entry.get())
        dist = float(dist_entry.get())
        fwhm = float(fwhm_entry.get())
        config = Config(linelistpath, save_folder, mol, mol_path, dist, fwhm, min_lamb, max_lamb, pix_per_fwhm,
                        intrinsic_line_width, cc)

        data_loader = DataLoader(config)
        data_loader.load_data()

        start_t = globals().get(f"t_{spanmol.lower()}")
        start_n_mol = globals().get(f"n_mol_{spanmol.lower()}")
        start_r = globals().get(f"{spanmol.lower()}_radius")

        model_fitting = ModelFitting(data_loader, config, data_field)
        model_fitting.message()
        result = model_fitting.fit_model(start_t, start_n_mol, start_r)

        # result_handler = ResultHandler(data_loader, config)

        T_best = np.round(result[0], decimals=1)
        R_best = np.round(result[2], decimals=2)
        N_best = format(10.0 ** result[1], '.3g')

        output_path = "../MODELS/"
        chi2_h2o = data_loader.chi2_h2o
        chi2 = chi2_h2o.chi2_total
        red_chi2 = chi2 / (len(chi2_h2o.measurements) - 3)

        result_tab = pd.DataFrame({
            'Model': spanmol.upper(),
            'T_best': [T_best],
            'N_best': [N_best],
            'R_best': [R_best],
            'Chi2_tot': [np.round(chi2, decimals=2)],
            'Chi2_red': [np.round(red_chi2, decimals=2)]
        })

        result_tab['Dist'] = dist
        result_tab['FWHM'] = fwhm
        result_tab['Wdt_intr'] = intrinsic_line_width
        result_tab.to_csv(f"{output_path}{spanmol.upper()}_slabfit_model_params.csv", index=False)

        svd_lns = pd.read_csv(linelistpath, sep=',')
        output = chi2_h2o.get_table
        svd_lns['Flux_model'] = output['flux_model']
        svd_lns['Chisquare'] = np.round(output['chi2'], decimals=2)

        # save output file with measurements as csv file
        svd_lns.to_csv(f"{output_path}{spanmol.upper()}_slabfit_fluxes.csv", header=True, index=False)

        exec(f"global t_{mol.lower()}; t_{mol.lower()} = {T_best}")
        exec(f"global {mol.lower()}_radius; {mol.lower()}_radius = {R_best}")
        exec(f"global n_mol_{mol.lower()}; n_mol_{mol.lower()} = {N_best}")

        eval(f"{mol.lower()}_temp_field").delete(0, "end")
        eval(f"{mol.lower()}_temp_field").insert(0, T_best)

        eval(f"{mol.lower()}_rad_field").delete(0, "end")
        eval(f"{mol.lower()}_rad_field").insert(0, R_best)

        eval(f"{mol.lower()}_dens_field").delete(0, "end")
        eval(f"{mol.lower()}_dens_field").insert(0, N_best)

        cet = globals()[f"{mol.lower()}_temp_field"]
        cer = globals()[f"{mol.lower()}_rad_field"]
        ced = globals()[f"{mol.lower()}_dens_field"]

        submit_temp(cet.get(), mol.lower())
        submit_rad(cer.get(), mol.lower())
        submit_col(ced.get(), mol.lower())

        pop_diagram()
        plt.draw(), canvas.draw()
        fig.canvas.flush_events()

        # Update the main GUI data_field
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'Slab fit completed!')


# -----------------------------------------------------------------------------
# NEEDS TO BE REFACTORED, HAS SOME GUI COMPONENTS
# -----------------------------------------------------------------------------

"""
Save() is connected to the "Save Line" button of the tool.
This function appends information of the the strongest line (as determined by intensity) in the spanned area graph to a csv file. 
The name of the csv file is set with the "svd_line_file" variable in the second code block above. 
For the parameters of the line that is saved, refer to the "line2save" variable in onselect().
When starting the tool up, the "headers" variable is set to False. After apending a line to the csv for the first time, the "headers" variable is changed to False.
"""


def Save():
    global line2save
    global headers
    global selectedline
    global linesavepath

    # This section is necessary for refreshing the text feed area to the left of the tool
    data_field.delete('1.0', "end")

    try:
        linesavepath
    except NameError:
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'Line save file is not defined!')
    else:
        if selectedline == True:  # "selectedline" variable is determined by whether or not an area was selected in the top graph or not

            line2save.to_csv(linesavepath, mode='a', index=False, header=False)

            data_field.insert('1.0', 'Line Saved!')
            fig.canvas.draw_idle()
        else:
            data_field.insert('1.0', 'No Line Selected!')
            fig.canvas.draw_idle()
            return

    canvas.draw()

# -----------------------------------------------------------------------------
# NEEDS TO BE REFACTORED, HAS SOME GUI COMPONENTS
# -----------------------------------------------------------------------------


def fitmulti_onselect():
    global selectedline, onselect_lines, deblend_filename

    if selectedline == True:  # "selectedline" variable is determined by whether or not an area was selected in the top graph or not
        print(' ')
        print('De-blending lines with LMFIT ...')
        onselect(data_region_x[1], data_region_x[-1])
        #onselect(xmin, xmax)

        mnwl = np.mean([data_region_x[0], data_region_x[-1]])
        deblend_filename = os.path.join(linesave_folder, f"{file_name}-deblended_{str(np.round(mnwl, decimals=3))}")
        #deblend_filename = 'LINESAVES/linedeblend_'+str(np.round(mnwl, decimals=3))+'.csv'

        # using one less pixel on each side here, because of how data_region_x is defined: to include 1 more pixel on each side
        gauss_fit = fitmulti_line(data_region_x[1], data_region_x[-2], onselect_lines['lam'])

        ln = [f'g{i + 1}' for i in range(len(onselect_lines['lam']))]
        output_lines = pd.DataFrame(onselect_lines).reset_index(drop=True)
        lines = np.array(onselect_lines['lam'])
        for i in range(len(onselect_lines['lam'])):
            # sigma_freq = ccum / (gauss_fit.params[ln + '_center'].value ** 2) * gauss_fit.params[ln + '_sigma'].value  # sigma from wavelength to frequency
            # gauss_area = gauss_fit.params[ln + '_height'].value * sigma_freq * np.sqrt (2 * np.pi) * (1.e-23)  # to get line flux in erg/s/cm2

            gauss_fwhm = gauss_fit.params[ln[i] + '_fwhm'].value / gauss_fit.params[
                ln[i] + '_center'].value * cc  # get FWHM in km/s
            # these if statements are made to avoid problems when the fit does not converge and stderr are returned as NoneType
            if gauss_fit.params[ln[i] + '_fwhm'].stderr is not None:
                gauss_fwhm_err = gauss_fit.params[ln[i] + '_fwhm'].stderr / gauss_fit.params[
                    ln[i] + '_center'].value * cc  # get FWHM error
            else:
                gauss_fwhm_err = float(fwhmtolerance_entry.get())

            sigma_freq = ccum / (gauss_fit.params[ln[i] + '_center'].value ** 2) * gauss_fit.params[ln[i] +
                                                                                                    '_sigma'].value  # sigma from wavelength to frequency
            if gauss_fit.params[ln[i] + '_sigma'].stderr is not None:
                sigma_freq_err = ccum / (gauss_fit.params[ln[i] + '_center'].value ** 2) * gauss_fit.params[ln[i] +
                                                                                                            '_sigma'].stderr  # error on sigma
            else:
                sigma_freq_err = np.nan

            gauss_area = gauss_fit.params[ln[i] + '_height'].value * sigma_freq * np.sqrt(2 * np.pi) * (
                1.e-23)  # to get line flux in erg/s/cm2
            if gauss_fit.params[ln[i] + '_height'].stderr is not None:
                gauss_area_err = np.absolute(gauss_area * np.sqrt(
                    (gauss_fit.params[ln[i] + '_height'].stderr / gauss_fit.params[ln[i] + '_height'].value) ** 2 +
                    (sigma_freq_err / sigma_freq) ** 2))  # get area error
            else:
                # measure error from data over the +/- 2 sigma range for each line
                flux_nofit, err_nofit = flux_integral(wave_data, flux_data, err_data,
                                                      gauss_fit.params[ln[i] + '_center'].value
                                                      - 2 * gauss_fit.params[ln[i] + '_sigma'].value,
                                                      gauss_fit.params[ln[i] + '_center'].value
                                                      + 2 * gauss_fit.params[ln[i] + '_sigma'].value)
                gauss_area_err = err_nofit

            output_lines.loc[i, "Flux_fit"] = np.float64(f'{gauss_area:.{3}e}')
            output_lines.loc[i, "Err_fit"] = np.float64(f'{gauss_area_err:.{3}e}')
            output_lines.loc[i, "FWHM_fit"] = np.round(gauss_fwhm, decimals=1)
            output_lines.loc[i, "FWHM_err"] = np.round(gauss_fwhm_err, decimals=1)
            output_lines.loc[i, "Centr_fit"] = np.round(gauss_fit.params[ln[i] + '_center'].value, decimals=5)
            if gauss_fit.params[ln[i] + '_center'].stderr is not None:
                output_lines.loc[i, "Centr_err"] = np.round(gauss_fit.params[ln[i] + '_center'].stderr, decimals=5)
            else:
                output_lines.loc[i, "Centr_err"] = float(centrtolerance_entry.get())
            output_lines.loc[i, "Doppler"] = np.round(
                (gauss_fit.params[ln[i] + '_center'].value - lines[i]) / lines[i] * cc, decimals=1)

        # save output file with measurements as csv file, update to use linesavepath
        output_lines.to_csv(deblend_filename + '.csv', header=True, index=False)

        fig.canvas.draw_idle()

        data_field.insert(tk.END, ('\n ' + "\nDe-blended line saved in /LINESAVES!"))

    else:
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'No Line Selected!')
        fig.canvas.draw_idle()
        return
    canvas.draw()


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------









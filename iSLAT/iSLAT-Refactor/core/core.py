# -----------------------------------------------------------------------------
# create HITRAN folder, only needed for first start
# -----------------------------------------------------------------------------

HITRAN_folder = "HITRANdata"
os.makedirs(HITRAN_folder, exist_ok=True)

variable_names = ['t_h2o', 'h2o_radius', 'n_mol_h2o', 't_oh', 'oh_radius', 'n_mol_oh', 't_hcn', 'hcn_radius',
                  'n_mol_hcn', 't_c2h2', 'c2h2_radius', 'n_mol_c2h2']

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------

selectfileinit()
print(' ')
print('Loading molecule files: ...')

molecules_data = read_from_user_csv()

for mol_name, mol_filepath, mol_label in molecules_data:
    # Import line lists from the ir_model folder
    mol_data = MolData(mol_name, mol_filepath)

    # Get the initial parameters for the current molecule, use default if not defined
    params = initial_parameters.get(mol_name, default_initial_params)
    scale_exponent = params["scale_exponent"]
    scale_number = params["scale_number"]
    t_kin = params["t_kin"]
    radius_init = params["radius_init"]

    # Calculate and set n_mol_init for the current molecule
    n_mol_init = float(scale_number * (10 ** scale_exponent))

    # Use exec() to create the variables with specific variable names for each molecule
    exec(f"mol_{mol_name.lower()} = MolData('{mol_name}', '{mol_filepath}')", globals())
    exec(f"scale_exponent_{mol_name.lower()} = {scale_exponent}", globals())
    exec(f"scale_number_{mol_name.lower()} = {scale_number}", globals())
    exec(f"n_mol_{mol_name.lower()}_init = {n_mol_init}", globals())
    exec(f"t_kin_{mol_name.lower()} = {t_kin}", globals())
    exec(f"{mol_name.lower()}_radius_init = {radius_init}", globals())

    # Print the results (you can modify this part as needed)
    print(f"Molecule Initialized: {mol_name}")
    # print(f"scale_exponent_{mol_name.lower()} = {scale_exponent}")
    # print(f"scale_number_{mol_name.lower()} = {scale_number}")
    # print(f"n_mol_{mol_name.lower()}_init = {n_mol_init}")
    # print(f"t_kin_{mol_name.lower()} = {t_kin}")
    # print(f"{mol_name.lower()}_radius_init = {radius_init}")
    # print()  # Empty line for spacing

    # Store the initial values in the dictionary
    initial_values[mol_name.lower()] = {
        "scale_exponent": scale_exponent,
        "scale_number": scale_number,
        "t_kin": t_kin,
        "radius_init": radius_init,
        "n_mol_init": n_mol_init
    }

# Initialize visibility booleans for each molecule
molecule_names = [mol_name.lower() for mol_name, _, _ in molecules_data]
for mol_name in molecule_names:
    if mol_name == 'h2o':
        globals()[f"{mol_name}_vis"] = True
    else:
        globals()[f"{mol_name}_vis"] = False

for mol_name, mol_filepath, mol_label in molecules_data:
    molecule_name_lower = mol_name.lower()

    # Column density
    exec(f"global n_mol_{molecule_name_lower}; n_mol_{molecule_name_lower} = n_mol_{molecule_name_lower}_init")

    # Temperature
    exec(f"global t_{molecule_name_lower}; t_{molecule_name_lower} = t_kin_{molecule_name_lower}")

    # Radius
    exec(f"global {molecule_name_lower}_radius; {molecule_name_lower}_radius = {molecule_name_lower}_radius_init")

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

skip = False
headers = True
selectedline = False

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

for mol_name, mol_filepath, mol_label in molecules_data:
    molecule_name_lower = mol_name.lower()

    # Intensity calculation
    exec(f"{molecule_name_lower}_intensity = Intensity(mol_{molecule_name_lower})")
    exec(
        f"{molecule_name_lower}_intensity.calc_intensity(t_kin_{molecule_name_lower}, n_mol_{molecule_name_lower}, dv=intrinsic_line_width)")

    # Spectrum creation
    exec(
        f"{molecule_name_lower}_spectrum = Spectrum(lam_min=min_lamb, lam_max=max_lamb, dlambda=model_pixel_res, R=model_line_width, distance=dist)")

    # Adding intensity to the spectrum
    exec(
        f"{molecule_name_lower}_spectrum.add_intensity({molecule_name_lower}_intensity, {molecule_name_lower}_radius ** 2 * np.pi)")

    # Fluxes and lambdas
    exec(
        f"fluxes_{molecule_name_lower} = {molecule_name_lower}_spectrum.flux_jy; lambdas_{molecule_name_lower} = {molecule_name_lower}_spectrum.lamgrid")


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
# Setting up the line identifier tool
int_pars = h2o_intensity.get_table
int_pars.index = range(len(int_pars.index))

write_default_csv(default_data)

csv_perm_path = os.path.join(save_folder, f"{file_name}-molsave.csv")
set_file_permissions(csv_perm_path, 0o666)  # Here, 0o666 sets read and write permissions for all users.


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
# NEEDS TO BE REFACTORED, HAS SOME GUI COMPONENTS
# -----------------------------------------------------------------------------

def fit_saved_lines():
    try:
        linelistpath
    except NameError:
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'Input line list is not defined!')
    else:
        try:
            linesavepath
        except NameError:
            data_field.delete('1.0', "end")
            data_field.insert('1.0', 'Output file is not defined!')
        else:
            svd_lns = pd.read_csv(linelistpath, sep=',')

            x_min = np.array(svd_lns['xmin'])
            x_max = np.array(svd_lns['xmax'])
            restwl = np.array(svd_lns['lam'])

            for i in range(len(x_min)):
                ax1.vlines(x_min[i], -2, 10, color='lime', alpha=0.5)
                ax1.vlines(x_max[i], -2, 10, color='lime', alpha=0.5)
                gauss_fit, gauss_fwhm, gauss_area, x_fit = fit_line(x_min[i], x_max[i])

                dely = gauss_fit.eval_uncertainty(sigma=3)
                ax1.fill_between(x_fit, gauss_fit.best_fit - dely, gauss_fit.best_fit + dely, color="#ABABAB",
                                 label=r'3-$\sigma$ uncertainty band')
                ax1.plot(x_fit, gauss_fit.best_fit, label='Gauss. fit', color='lime', ls='--')
                flux_nofit, err_nofit = flux_integral(wave_data, flux_data, err_data, x_min[i], x_max[i])

                sig_det_lim = 2
                # these reformatting below is for reducing the number of decimals and then get back to a float
                svd_lns.loc[i, "Flux_data"] = np.float64(f'{flux_nofit:.{3}e}')
                svd_lns.loc[i, "Err_data"] = np.float64(f'{err_nofit:.{3}e}')
                svd_lns.loc[i, "Line_SN"] = np.round(flux_nofit / err_nofit, decimals=1)
                if np.absolute(flux_nofit) > sig_det_lim * err_nofit:  # determine line detection based on data
                    svd_lns.loc[i, "Line_det"] = np.bool_(True)
                else:
                    svd_lns.loc[i, "Line_det"] = np.bool_(False)
                # store as "islat" values the data values, unless the fit results are detected and replaced below
                svd_lns.loc[i, "Flux_islat"] = svd_lns.loc[i, "Flux_data"]
                svd_lns.loc[i, "Err_islat"] = svd_lns.loc[i, "Err_data"]

                # store fit results only if fit is good and line is detected; for now we're using a condition on line detection, as the goodness of fit is not very informative in MIRI spectra, it seems..
                svd_lns.loc[i, "Fit_SN"] = np.round(gauss_area[0] / gauss_area[1], decimals=1)
                if np.absolute(gauss_area[0]) > sig_det_lim * gauss_area[1]:
                    svd_lns.loc[i, "Fit_det"] = np.bool_(True)
                    svd_lns.loc[i, "Flux_fit"] = np.float64(f'{gauss_area[0]:.{3}e}')
                    svd_lns.loc[i, "Err_fit"] = np.float64(f'{gauss_area[1]:.{3}e}')
                    svd_lns.loc[i, "Flux_islat"] = np.float64(f'{gauss_area[0]:.{3}e}')
                    svd_lns.loc[i, "Err_islat"] = np.float64(f'{gauss_area[1]:.{3}e}')
                    svd_lns.loc[i, "FWHM_fit"] = np.round(gauss_fwhm[0], decimals=1)
                    svd_lns.loc[i, "FWHM_err"] = np.round(gauss_fwhm[1], decimals=1)
                    svd_lns.loc[i, "Centr_fit"] = np.round(gauss_fit.params['center'].value, decimals=5)
                    svd_lns.loc[i, "Centr_err"] = np.round(gauss_fit.params['center'].stderr, decimals=5)
                    svd_lns.loc[i, "Doppler"] = np.round(
                        (gauss_fit.params['center'].value - restwl[i]) / restwl[i] * cc, decimals=1)

                else:
                    svd_lns.loc[i, "Fit_det"] = np.bool_(False)
                    svd_lns.loc[i, "Flux_fit"] = np.float64(f'{gauss_area[0]:.{3}e}')
                    svd_lns.loc[i, "Err_fit"] = np.float64(f'{gauss_area[1]:.{3}e}')
                    svd_lns.loc[i, "FWHM_fit"] = np.nan
                    svd_lns.loc[i, "FWHM_err"] = np.nan
                    svd_lns.loc[i, "Centr_fit"] = np.nan
                    svd_lns.loc[i, "Centr_err"] = np.nan
                    svd_lns.loc[i, "Doppler"] = np.nan

                svd_lns.loc[i, "Red-chisq"] = np.round(gauss_fit.redchi, decimals=2)

            # add rotation diagram values
            freq = ccum / svd_lns['lam']
            svd_lns['RD_y'] = np.round(
                np.log(4 * np.pi * svd_lns["Flux_fit"] / (svd_lns['a_stein'] * hh * freq * svd_lns['g_up'])),
                decimals=3)

            # save output file with measurements as csv file
            svd_lns.to_csv(linesavepath, header=True, index=False)

            data_field.delete('1.0', "end")
            data_field.insert('1.0', 'Input lines fitted and saved.')
            canvas.draw()

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------

"""
on_xlims_change() saves the current xp1 and xp2 for use in other functions.
This Function is necessary to allow the user to use matplotlib's interactive graph scrolling feature without 
breaking the functionality of other features of this tool (e.g. Next() or Prev())
"""


def on_xlims_change(event_ax):
    global xp1
    global xp2
    xp1, xp2 = event_ax.get_xlim()

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
    
"""
flux_integral() calculates the flux of the data line in the selected region of the top graph.
This function is used in onselect().
"""


def flux_integral(lam, flux, err, lam_min, lam_max):
    # calculate flux integral
    integral_range = np.where(np.logical_and(lam > lam_min, lam < lam_max))
    line_flux_meas = np.trapz(flux[integral_range[::-1]], x=ccum / lam[integral_range[::-1]])
    line_flux_meas = -line_flux_meas * 1e-23  # to get (erg s-1 cm-2); it's using frequency array, so need the - in front of it
    line_err_meas = np.trapz(err[integral_range[::-1]], x=ccum / lam[integral_range[::-1]])
    line_err_meas = -line_err_meas * 1e-23  # to get (erg s-1 cm-2); it's using frequency array, so need the - in front of it
    return line_flux_meas, line_err_meas

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
def update_xp1_rng():
    global xp1, rng, xp2
    # Get the values from the Tkinter Entry widgets and convert them to floats
    min_lamb = float(min_lamb_entry.get())
    max_lamb = float(max_lamb_entry.get())
    xp1 = float(xp1_entry.get())
    rng = float(rng_entry.get())
    xp2 = xp1 + rng
    if xp1 < min_lamb or xp1 > max_lamb:
        if xp1 < min_lamb:
            min_lamb = xp1
            min_lamb_entry.delete(0, "end")
            min_lamb_entry.insert(0, str(min_lamb))
        if xp1 > max_lamb:
            max_lamb = xp2
            max_lamb_entry.delete(0, "end")
            max_lamb_entry.insert(0, str(max_lamb))
        update_initvals()
    ax1.set_xlim(xmin=xp1, xmax=xp2)
    print("Updated values: xp1 =", xp1, ", rng =", rng)
    update()
    canvas.draw()
# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
def update_initvals():
    global min_lamb, max_lamb, dist, fwhm, star_rv, model_line_width, model_pixel_res, intrinsic_line_width, wave_data, pix_per_fwhm
    # Get the values from the Tkinter Entry widgets and convert them to floats
    min_lamb = float(min_lamb_entry.get())
    max_lamb = float(max_lamb_entry.get())
    dist = float(dist_entry.get())
    fwhm = float(fwhm_entry.get())
    if fwhm >= 70:
        pix_per_fwhm = 10
    if fwhm < 70:
        pix_per_fwhm = 20  # increase model pixel sampling in case of higher resolution spectra, usually in the M band
    intrinsic_line_width = float(intrinsic_line_width_entry.get())
    model_line_width = cc / fwhm
    model_pixel_res = (np.mean([min_lamb, max_lamb]) / cc * fwhm) / pix_per_fwhm
    # this below needs to be updated to act on the wave array in the data
    wave_data = wave_original - (wave_original / cc * float(star_rv_entry.get()))
    loadsavedmessage()
    update()
    canvas.draw()

    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Parameter updated!')
    # time.sleep(2)

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------

def update_csv():
    filename = os.path.join(save_folder, f"{file_name}-molsave.csv")
    csv_file = filename
    try:
        # Read existing data from CSV
        with open(csv_file, 'r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

        # Identify the row to delete
        for i, row in enumerate(rows):
            if row[0].lower() == mol_name:
                del rows[i]
                break

        # Write updated data back to CSV
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        print(f"{csv_file} updated.")
    except Exception as e:
        print(f"Error updating {csv_file}: {e}")

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------

def saveparams_button_clicked():
    write_to_csv(molecules_data, True)

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------

def write_default_csv(data):
    csv_filename = os.path.join(save_folder, f"default.csv")

    try:
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header = ['Molecule Name', 'File Path', 'Molecule Label', 'Temp', 'Rad', 'N_Mol', 'Vis']
            writer.writerow(header)

            for mol_name, mol_filepath, mol_label in data:
                row = [mol_name, mol_filepath, mol_label]
                # Append the variables for the current molecule to the row
                row.append(globals().get(f"t_{mol_name.lower()}", ''))
                row.append(globals().get(f"{mol_name.lower()}_radius", ''))
                row.append(globals().get(f"n_mol_{mol_name.lower()}", ''))
                row.append(globals().get(f"{mol_name.lower()}_vis", ''))
                writer.writerow(row)
    except Exception as e:
        print("Error:", e)

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
        
# Function to open spectrum data file from the GUI using Open File for "Spectrum data file"
def selectfile():
    global file_path
    global file_name
    global wave_data, flux_data, err_data, wave_original
    global input_spectrum_data
    global filename_box_data
    global xp1, rng, xp2, xp1_entry, rng_entry

    filetypes = [('CSV Files', '*.csv')]
    spectra_directory = os.path.abspath("../EXAMPLE-data")
    infiles = filedialog.askopenfilename(multiple=True, title='Choose Spectrum Data File', filetypes=filetypes,
                                         initialdir=spectra_directory)

    if infiles:
        for file_path in infiles:
            # Process each selected file
            print("Selected file:", file_path)
            file_name = os.path.basename(file_path)

            file_name_label.config(text=str(file_name))
            # filename_box_data.set_val(file_name)
            # Add your code to process each file
            # THIS IS THE OLD FILE SYSTEM (THIS WILL BE USED UNTIL THE NEW FILE SYSTEM IS DEVELOPED) USE THIS!!!!!
            input_spectrum_data = pd.read_csv(filepath_or_buffer=(file_path), sep=',')
            wave_data = np.array(input_spectrum_data['wave'])
            wave_original = np.array(input_spectrum_data['wave'])
            flux_data = np.array(input_spectrum_data['flux'])
            if 'err' in input_spectrum_data:
                err_data = np.array(input_spectrum_data['err'])
            else:
                err_data = np.full_like(flux_data, np.nanmedian(flux_data) / 100)  # assumed, if not present

            # Set new values of xp1 and rng only if the new spectrum is in a different wave range
            fig_max_limit = np.nanmax(wave_data)
            fig_min_limit = np.nanmin(wave_data)
            xp1_current = float(xp1_entry.get())
            if xp1_current > fig_max_limit or xp1_current < fig_min_limit:
                xp1 = fig_min_limit + (fig_max_limit - fig_min_limit) / 2
                rng = (fig_max_limit - fig_min_limit) / 10
                xp2 = xp1 + rng
                xp1_entry.delete(0, "end")
                xp1_entry.insert(0, np.around(xp1, decimals=2))
                rng_entry.delete(0, "end")
                rng_entry.insert(0, np.around(rng, decimals=2))

            # now = dt.now()
            # dateandtime = now.strftime("%d-%m-%Y-%H-%M-%S")
            # print(dateandtime)
            # svd_line_file = f'savedlines-{dateandtime}.csv'

            update()

            data_field.delete('1.0', "end")
            data_field.insert('1.0', 'New spectrum loaded!')
    else:
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'No file selected.')


# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
        
def selectlinefile():
    global linelistfile
    global linelistpath

    # Create the folder if it doesn't exist
    linelist_folder = "LINELISTS"

    # Set the initial directory to the created folder
    initial_directory = os.path.abspath(linelist_folder)

    filetypes = [('CSV Files', '*.csv')]
    infile = filedialog.askopenfilename(
        title='Choose Line List File',
        filetypes=filetypes,
        defaultextension=".csv",
        initialdir=initial_directory  # Set the initial directory
    )

    if infile:
        linelistpath = infile
        linelistfile = os.path.basename(linelistpath)
        # Update the label with the selected/created file
        linefile_name_label.config(text=str(linelistfile))

        # headers = "lev_up,lev_low,lam, tau,intens,a_stein,e_up,g_up,xmin,xmax"

        # Check if the file already exists
        if os.path.exists(infile):
            # File already exists, so check if the headers match
            with open(infile, 'r') as existing_file:
                first_line = existing_file.readline().strip()
            # if first_line == headers:
            #    # Headers match, no need to write them
            #    pass
            # else:
            #    print("File selected is not a line save file")
        else:
            # File doesn't exist
            print("File selected does not exist")

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
            
def savelinefile():
    global linesavefile
    global linesavepath

    # Set the initial directory to the created folder
    initial_directory = os.path.abspath(linesave_folder)

    filetypes = [('CSV Files', '*.csv')]
    infile = filedialog.asksaveasfilename(
        title='Choose or Define a File',
        filetypes=filetypes,
        defaultextension=".csv",
        initialdir=initial_directory  # Set the initial directory
    )

    if infile:
        linesavepath = infile
        linesavefile = os.path.basename(linesavepath)
        # Update the label with the selected/created file
        savelinefile_name_label.config(text=str(linesavefile))

        headers = "species,lev_up,lev_low,lam,tau,intens,a_stein,e_up,g_up,xmin,xmax"

        # Check if the file already exists
        if os.path.exists(infile):
            # File already exists, so check if the headers match
            with open(infile, 'r') as existing_file:
                first_line = existing_file.readline().strip()
            if first_line == headers:
                # Headers match, no need to write them
                pass
            elif not first_line:
                # First line is empty, so write the headers
                with open(infile, 'a') as file:
                    file.write(headers + '\n')
            else:
                print("File selected is not a line save file")
        else:
            # File doesn't exist, create a new one and write headers
            with open(infile, 'w') as file:
                file.write(headers + '\n')

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
                
def generate_all_csv():
    for molecule in molecules_data:
        mol_name = molecule[0]
        mol_name_lower = mol_name.lower()

        fluxes = globals().get(f'fluxes_{mol_name_lower}', np.array([]))
        lambdas = globals().get(f'lambdas_{mol_name_lower}', np.array([]))

        if fluxes.size == 0 or lambdas.size == 0 or len(fluxes) != len(lambdas):
            continue

        data = list(zip(lambdas, fluxes))

        os.makedirs(output_dir, exist_ok=True)

        csv_file_path = os.path.join(output_dir, f"{mol_name}_spec_output.csv")

        with open(csv_file_path, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["wave", "flux"])
            for row in data:
                csv_writer.writerow(row)

    # Get the fluxes and lambdas for the selected molecule
    fluxes = globals().get('total_fluxes', [])
    lambdas = globals().get('lambdas_h2o', np.array([]))

    if len(fluxes) == 0 or lambdas.size == 0 or len(fluxes) != len(lambdas):
        return

    # Combine fluxes and lambdas into rows
    data = list(zip(lambdas, fluxes))

    # Create a directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Specify the full path for the CSV file
    csv_file_path = os.path.join(output_dir, "SUM_spec_output.csv")

    # Create a CSV file with the selected data in the "MODELS" directory
    with open(csv_file_path, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["wave", "flux"])
        for row in data:
            csv_writer.writerow(row)

    data_field.delete('1.0', "end")
    data_field.insert('1.0', f'All models exported into iSLAT/MODELS!')

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
                
def generate_csv(mol_name):
    if mol_name == "SUM":

        # Get the fluxes and lambdas for the selected molecule
        fluxes = globals().get('total_fluxes', [])
        lambdas = globals().get('lambdas_h2o', np.array([]))

        if len(fluxes) == 0 or lambdas.size == 0 or len(fluxes) != len(lambdas):
            return

        # Combine fluxes and lambdas into rows
        data = list(zip(lambdas, fluxes))

        # Create a directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Specify the full path for the CSV file
        csv_file_path = os.path.join(output_dir, "SUM_spec_output.csv")

        # Create a CSV file with the selected data in the "MODELS" directory
        with open(csv_file_path, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["wave", "flux"])
            for row in data:
                csv_writer.writerow(row)

        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'SUM model exported into iSLAT/MODELS!')

    if mol_name == "ALL":
        generate_all_csv()

    else:
        # Find the tuple for the selected molecule
        molecule = next((m for m in molecules_data if m[0] == mol_name), None)
        if molecule is None:
            return

        # Extract the lowercase version of the molecule name
        mol_name_lower = mol_name.lower()

        # Get the fluxes and lambdas for the selected molecule
        fluxes = globals().get(f'fluxes_{mol_name_lower}', np.array([]))
        lambdas = globals().get(f'lambdas_{mol_name_lower}', np.array([]))
        line_prop = eval(f"{mol_name.lower()}_intensity.get_table")
        line_prop.to_csv(output_dir + '/' + f"{mol_name}_line_params.csv", index=False)

        if fluxes.size == 0 or lambdas.size == 0 or len(fluxes) != len(lambdas):
            return

        # Combine fluxes and lambdas into rows
        data = list(zip(lambdas, fluxes))
        # Create a directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Specify the full path for the CSV file
        csv_file_path = os.path.join(output_dir, f"{mol_name}_spec_output.csv")

        # Create a CSV file with the selected data in the "MODELS" directory
        with open(csv_file_path, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["wave", "flux"])
            for row in data:
                csv_writer.writerow(row)

        data_field.delete('1.0', "end")
        data_field.insert('1.0', f'{mol_name} model exported into iSLAT/MODELS!')

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
        
def import_molecule():
    MoleculeSelector(root, data_field)

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
    
def set_file_permissions(filename, mode):
    print(' ')
    print('Molecule paths file: ...')

    try:
        os.chmod(filename, mode)
        print(f"Permissions set for {filename}")
    except Exception as e:
        print(f"File not found, permissions will be set when molecules are saved")


# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
    
def write_to_csv(data, confirmation=False):
    if confirmation:
        # Display a confirmation dialog
        confirmed = tk.messagebox.askquestion("Confirmation",
                                              "Sure you want to save? This will overwrite any previous save for this data file.")
        if confirmed == "no":  # Check if user clicked "no"
            return

    csv_filename = os.path.join(save_folder, f"{file_name}-molsave.csv")

    try:
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header = ['Molecule Name', 'File Path', 'Molecule Label', 'Temp', 'Rad', 'N_Mol', 'Color', 'Vis', 'Dist',
                      'StellarRV', 'FWHM', 'Broad']
            writer.writerow(header)

            for mol_name, mol_filepath, mol_label in data:
                row = [mol_name, mol_filepath, mol_label]
                linevar = eval(f"{mol_name.lower()}_line")
                linecolor = linevar.get_color()
                # Append the variables for the current molecule to the row
                row.append(globals().get(f"t_{mol_name.lower()}", ''))
                row.append(globals().get(f"{mol_name.lower()}_radius", ''))
                row.append(globals().get(f"n_mol_{mol_name.lower()}", ''))
                row.append(linecolor)
                row.append(globals().get(f"{mol_name.lower()}_vis", ''))
                row.append(dist)
                row.append(star_rv_entry.get())
                row.append(fwhm)
                row.append(intrinsic_line_width)

                writer.writerow(row)

        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'Molecule parameters saved into file.')
        fig.canvas.draw_idle()
    except Exception as e:
        print("Error:", e)

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
        
def write_user_csv(data):
    csv_filename = os.path.join(save_folder, f"molecules_list.csv")

    try:
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header = ['Molecule Name', 'File Path', 'Molecule Label', 'Temp', 'Rad', 'N_Mol', 'Color', 'Vis', 'Dist',
                      'StellarRV', 'FWHM', 'Broad']
            writer.writerow(header)

            for mol_name, mol_filepath, mol_label in data:
                row = [mol_name, mol_filepath, mol_label]
                linevar = eval(f"{mol_name.lower()}_line")
                linecolor = linevar.get_color()
                # Append the variables for the current molecule to the row
                row.append(globals().get(f"t_{mol_name.lower()}", ''))
                row.append(globals().get(f"{mol_name.lower()}_radius", ''))
                row.append(globals().get(f"n_mol_{mol_name.lower()}", ''))
                row.append(linecolor)
                row.append(globals().get(f"{mol_name.lower()}_vis", ''))
                row.append(dist)
                row.append(star_rv_entry.get())
                row.append(fwhm)
                row.append(intrinsic_line_width)

                writer.writerow(row)

        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'Molecule parameters saved into file.')
        fig.canvas.draw_idle()
    except Exception as e:
        print("Error:", e)

# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
        
def down_molecule_data(val):
    url = "https://hitran.org/lbl/"
    browsers = ["chrome", "edge", "firefox", "safari"]

    for browser_name in browsers:
        try:
            # Attempt to open the URL using webbrowser
            webbrowser.get(browser_name).open(url)
            break  # Stop trying if the browser opens the URL successfully
        except webbrowser.Error:
            try:
                # Fallback to using 'os' to execute the browser's command directly
                os.system(f"{browser_name} {url}")
                break  # Stop trying if the command succeeds
            except OSError:
                continue  # Try the next browser if the current one fails       


# -----------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------
        
# Define the span selecting function of the tool
span = SpanSelector(
    ax1,
    onselect,
    "horizontal",
    useblit=False,
    props=dict(alpha=0.5, facecolor="lime"),
    interactive=True,
    drag_from_anywhere=True
)



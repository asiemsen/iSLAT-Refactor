#for functions that need to be seperated in responsibilities

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
def fit_onselect():
    global selectedline

    print(' ')
    print('Fitting line with LMFIT ...')

    if selectedline == True:  # "selectedline" variable is determined by whether or not an area was selected in the top graph or not

        # using one less pixel on each side here, because of how data_region_x is defined: to include 1 more pixel on each side
        gauss_fit, gauss_fwhm, gauss_area, x_fit = fit_line(data_region_x[1], data_region_x[-2])

        dely = gauss_fit.eval_uncertainty(sigma=3)
        ax2.fill_between(x_fit, gauss_fit.best_fit - dely, gauss_fit.best_fit + dely, color="#ABABAB",
                         label=r'3-$\sigma$ uncertainty band')
        ax2.plot(x_fit, gauss_fit.best_fit, label='Gauss. fit', color='lime', ls='--')

        data_field.insert(tk.END, ('\n ' + '\nGaussian fit results: ' + '\nCentroid (μm) = ' + str(
            np.round(gauss_fit.params['center'].value, decimals=5)) + ' +/- ' + str(
            np.round(gauss_fit.params['center'].stderr, decimals=5)) + '\nFWHM (km/s) = ' + str(
            np.round(gauss_fwhm[0], decimals=1)) + ' +/- ' + str(
            np.round(gauss_fwhm[1], decimals=1)) + '\nArea (erg/s/cm2) = ' + f'{gauss_area[0]:.{3}e}' +
                                   ' +/- ' + f'{gauss_area[1]:.{3}e}'))

        fig.canvas.draw_idle()
    else:
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'No Line Selected!')
        fig.canvas.draw_idle()
        return
    canvas.draw()




"""
multifit_line() uses LMFIT to fit a line and provide best-fit parameters.
"""

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
def fitmulti_line(xmin, xmax, onsel_lines):
    global deblend_filename

    fit_range = np.where(np.logical_and(wave_data >= xmin, wave_data <= xmax))  # define spectral range for the fit
    x_fit = wave_data[fit_range[::-1]]  # reverse the wavelength array to use it in the fit
    y_fit = flux_data[fit_range[::-1]]
    err_fit = err_data[fit_range[::-1]]
    # re-sample data if not enough datapoints for the fit (defining number of free parameters here):
    freeparams = 3
    if len(x_fit) < len(onsel_lines) * freeparams:
        x_fit_new = np.linspace(np.min(x_fit), np.max(x_fit), num=len(onsel_lines) * freeparams)
        y_fit_new = np.interp(x_fit_new, x_fit, y_fit)
        err_fit_new = np.interp(x_fit_new, x_fit, err_fit)
        x_fit = x_fit_new
        y_fit = y_fit_new
        err_fit = err_fit_new
        ax2.plot(x_fit, y_fit, '--', color='grey')

    fwhm = float(fwhm_entry.get())
    fwhm_um = np.mean([xmin, xmax]) / cc * fwhm
    sig = fwhm_um / 2.35482
    sig_tol = (np.mean([xmin, xmax]) / cc * float(fwhmtolerance_entry.get())) / 2.35482

    #lines = np.sort(onsel_lines) # sort to make sure it's in increasing order
    lines = np.array(onsel_lines)
    wl_tol = float(centrtolerance_entry.get())

    # initial guess for amplitude, using total integrated flux divided by number of lines (and conversion factor)
    Garea = flux_integral(x_fit, y_fit, err_fit, xmin, xmax)
    Garea_fg = Garea[0] / len(lines) * 1e11

    fwhm_vary = True
    if sig_tol == 0: fwhm_vary = False
    centr_vary = True
    if wl_tol == 0: centr_vary = False

    gauss1 = GaussianModel(prefix='g1_')
    pars = gauss1.guess(y_fit, x=x_fit)
    pars.update(
        gauss1.make_params(center=dict(value=lines[0], vary=centr_vary, min=lines[0] - wl_tol, max=lines[0] + wl_tol),
                           sigma=dict(value=sig, vary=fwhm_vary, min=sig - sig_tol, max=sig + sig_tol),
                           amplitude=dict(value=Garea_fg, min=0)))
    mod = gauss1

    for i in range(len(lines) - 1):
        gauss_tmp = GaussianModel(prefix='g' + str(i + 2) + '_')
        pars.update(gauss_tmp.make_params(
            center=dict(value=lines[i + 1], vary=centr_vary, min=lines[i + 1] - wl_tol, max=lines[i + 1] + wl_tol),
            sigma=dict(value=sig, vary=fwhm_vary, min=sig - sig_tol, max=sig + sig_tol),
            amplitude=dict(value=Garea_fg, min=0)))
        mod = mod + gauss_tmp

    init = mod.eval(pars, x=x_fit)
    fitmethod = 'leastsq'  # 'leastsq'  'emcee'
    gauss_fit = mod.fit(y_fit, pars, x=x_fit, weights=1 / err_fit, method=fitmethod)  # , steps=5000

    print(gauss_fit.fit_report())

    comps = gauss_fit.eval_components(x=x_fit)
    ax2.plot(x_fit, gauss_fit.best_fit, '--', color='red', linewidth=3, label='Total fit')
    for i in range(len(lines)):
        ind = i + 1
        ax2.plot(x_fit, comps['g' + str(ind) + '_'], '--', label='Line #' + str(ind))
        ax2.vlines(gauss_fit.params['g' + str(ind) + '_center'], 0, gauss_fit.params['g' + str(ind) + '_height'],
                   linestyles=':', color='Grey')
    ax2.legend()
    plt.savefig(deblend_filename + '.pdf', bbox_inches='tight', dpi=10)
    #plt.savefig(deblend_filename+'.jpg', dpi = 100, optimize = True, progressive = True)

    deblend_models = pd.DataFrame({'wave': x_fit,
                                   'flux': y_fit,
                                   'err': err_fit,
                                   'gTOT': gauss_fit.best_fit,
                                   })
    for i in range(len(lines)):
        ind = i + 1
        deblend_models['g' + str(ind) + '_'] = comps['g' + str(ind) + '_']
    deblend_models.to_csv(deblend_filename + '_models.csv', header=True,
                          index=False)

    return gauss_fit

# -----------------------------------------------------------------------------
#

"""
fit_line() uses LMFIT to fit a line and provide best-fit parameters.
"""


def fit_line(xmin, xmax):
    fit_range = np.where(np.logical_and(wave_data >= xmin, wave_data <= xmax))  # define spectral range for the fit
    x_fit = wave_data[fit_range[::-1]]  # reverse the wavelength array to use it in the fit
    model = GaussianModel()  # use gaussian model from LMFIT
    # model = PseudoVoigtModel()
    params = model.guess(flux_data[fit_range[::-1]], x=x_fit)  # get initial guess for parameters
    # the fit in the next line uses the data error array as weights, as described in the LMFIT docs and this discussion: https://groups.google.com/g/lmfit-py/c/SmO19HbXGcc/m/xa3tsPJcBgAJ
    gauss_fit = model.fit(flux_data[fit_range[::-1]], params, x=x_fit, weights=1 / err_data[fit_range[::-1]],
                          nan_policy='omit')  # make the fit, ignoring nans
    print(gauss_fit.fit_report())  # print full fit report

    gauss_fwhm = gauss_fit.params['fwhm'].value / gauss_fit.params['center'].value * cc  # get FWHM in km/s
    # these if statements are made to avoid problems when the fit does not converge and stderr are returned as NoneType
    if gauss_fit.params['fwhm'].stderr is not None:
        gauss_fwhm_err = gauss_fit.params['fwhm'].stderr / gauss_fit.params['center'].value * cc  # get FWHM error
    else:
        gauss_fwhm_err = np.nan

    sigma_freq = ccum / (gauss_fit.params['center'].value ** 2) * gauss_fit.params[
        'sigma'].value  # sigma from wavelength to frequency
    if gauss_fit.params['sigma'].stderr is not None:
        sigma_freq_err = ccum / (gauss_fit.params['center'].value ** 2) * gauss_fit.params[
            'sigma'].stderr  # error on sigma
    else:
        sigma_freq_err = np.nan

    gauss_area = gauss_fit.params['height'].value * sigma_freq * np.sqrt(2 * np.pi) * (
        1.e-23)  # to get line flux in erg/s/cm2
    if gauss_fit.params['height'].stderr is not None:
        gauss_area_err = np.absolute(gauss_area * np.sqrt(
            (gauss_fit.params['height'].stderr / gauss_fit.params['height'].value) ** 2 +
            (sigma_freq_err / sigma_freq) ** 2))  # get area error
    else:
        gauss_area_err = np.nan

    return gauss_fit, [gauss_fwhm, gauss_fwhm_err], [gauss_area, gauss_area_err], x_fit

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def update(*val):
    global skip  # See reference in reset()
    # If skip is False, then update() does not run. This cuts down needless processing
    if skip == True:
        return

    ax1.clear()  # Reference: matplotlib.widgets
    ax2.clear()  # These functions clear the three plots of the tool
    ax3.clear()  # They are rebuilt in the update() function

    global xp1, xp2, span, model_line_select, data_line_select, fig_height, fig_bottom_height, n_mol, selectedline, spanmol, sum_line, int_pars, molecules_data, total_fluxes, dist, fwhm, max_lamb, min_lamb

    span.set_visible(
        False)  # Clears the blue area created by the span selector (range selector in the top graph of the tool)
    selectedline = False  # See reference in save()

    # Clearing the text feed box.
    data_field.delete('1.0', "end")
    # Make empty lines for the second plot
    data_line_select, = ax2.plot([], [], color=foreground, linewidth=2)
    data_line, = ax1.plot([], [], color=foreground, linewidth=1)
    ax1.errorbar(wave_data, flux_data, yerr=err_data, fmt='None', ecolor='gray', elinewidth=1, zorder=-1)
    data_line.set_label('Data')

    ax1.set_prop_cycle(color=['dodgerblue', 'darkorange', 'orangered', 'limegreen', 'mediumorchid', 'magenta',
                              'hotpink', 'cyan', 'gold', 'turquoise', 'chocolate', 'royalblue', 'sienna', 'lime',
                              'darkviolet', 'blue'])

    # Make empty lines for the top graph for each molecule
    for mol_name, mol_filepath, mol_label in molecules_data:
        molecule_name_lower = mol_name.lower()

        if molecule_name_lower in deleted_molecules:
            continue

        exec(f"{molecule_name_lower}_line, = ax1.plot([], [], alpha=1, linewidth=2, ls='--')", globals())
        exec(f"{molecule_name_lower}_line.set_label('{mol_label}')", globals())

        try:
            color_var = globals().get(f"{molecule_name_lower}_color")

            if color_var:
                # Set the color of the molecule line
                exec(f"{molecule_name_lower}_line.set_color('{color_var}')", globals())
                exec(f"global {molecule_name_lower}_line_color; {molecule_name_lower}_line_color = '{color_var}'")
        except NameError:
            print('not changed!')
            return

    # sum_line, = ax1.plot([], [], color='gray', linewidth=1)
    # sum_line.set_label('Sum')
    ax1.legend()

    # h2o, oh, hcn, and c2h2 are variables that are set to True or false depending if the molecule is currently selected in the tool
    # If True, then that molecule's model is rebuilt with any new conditions (as set by the sliders or text input) that may have called the update() function
    # See h2o_select()
    for mol_name, mol_filepath, mol_label in molecules_data:
        molecule_name_lower = mol_name.lower()

        # Intensity calculation
        exec(
            f"{molecule_name_lower}_intensity.calc_intensity(t_{molecule_name_lower}, n_mol_{molecule_name_lower}, dv=intrinsic_line_width)",
            globals())

        # Spectrum creation
        exec(
            f"{molecule_name_lower}_spectrum = Spectrum(lam_min=min_lamb, lam_max=max_lamb, dlambda=model_pixel_res, R=model_line_width, distance=dist)",
            globals())

        # Adding intensity to the spectrum
        exec(
            f"{molecule_name_lower}_spectrum.add_intensity({molecule_name_lower}_intensity, {molecule_name_lower}_radius ** 2 * np.pi)",
            globals())

        # Fluxes and lambdas
        exec(
            f"fluxes_{molecule_name_lower} = {molecule_name_lower}_spectrum.flux_jy; lambdas_{molecule_name_lower} = {molecule_name_lower}_spectrum.lamgrid",
            globals())

        linevar = eval(f"{molecule_name_lower}_line")
        linecolor = linevar.get_color()
        exec(f"global {molecule_name_lower}_line_color; {mol_name.lower()}_line_color = '{linecolor}'")

    # Redefining plot parameters that were deleted by the clear functions at the begining of this function
    ax1.set_ylabel('Flux density (Jy)')
    ax1.set_xlabel('Wavelength (μm)')
    ax2.set_ylabel('Flux density (Jy)')
    ax2.set_xlabel('Wavelength (μm)')
    plt.rcParams['font.size'] = 10

    # xp1 and xp2 define the range of spectrum shown in the top graph
    # See Prev(), Next(), and on_xlims_change()
    # Originally defined in code block below
    ax1.set_xlim(xmin=xp1, xmax=xp2)

    # Scaling the y-axis based on tallest peak of data in the range of xp1 and xp2
    range_flux_cnts = input_spectrum_data[(input_spectrum_data['wave'] > xp1) & (input_spectrum_data['wave'] < xp2)]
    if range_flux_cnts.empty:
        fig_height = np.nanmax(total_fluxes)
        fig_bottom_height = 0
    else:
        range_flux_cnts.index = range(len(range_flux_cnts.index))
        fig_height = np.nanmax(range_flux_cnts.flux)
        fig_bottom_height = np.nanmin(range_flux_cnts.flux)
    ax1.set_ylim(ymin=fig_bottom_height, ymax=fig_height + (fig_height / 8))

    # Initialize total fluxes list
    total_fluxes = []
    # Calculate total fluxes based on visibility conditions
    for i in range(len(lambdas_h2o)):
        flux_sum = 0
        for mol_name, mol_filepath, mol_label in molecules_data:

            mol_name_lower = mol_name.lower()
            visibility_flag = f"{mol_name_lower}_vis"
            fluxes_molecule = f"fluxes_{mol_name_lower}"

            if visibility_flag in globals() and globals()[visibility_flag]:
                flux_sum += globals()[fluxes_molecule][i]

        total_fluxes.append(flux_sum)

    if mode == True:
        ax1.fill_between(lambdas_h2o, total_fluxes, color='gray', alpha=1)

    if mode == False:
        ax1.fill_between(lambdas_h2o, total_fluxes, color='lightgray', alpha=1)

    # populating the empty lines created earlier in the function
    for mol_name, mol_filepath, mol_label in molecules_data:
        molecule_name_lower = mol_name.lower()

        # Dynamically set the data for each molecule's line using exec and globals()
        exec(f"{molecule_name_lower}_line.set_data(lambdas_{molecule_name_lower}, fluxes_{molecule_name_lower})",
             globals())
    data_line.set_data(wave_data, flux_data)

    # This is the opacity value that will be used for all shades (if you want to change the opacity just change this value)
    alpha_set = .2

    for mol_name, mol_filepath, mol_label in molecules_data:
        molecule_name_lower = mol_name.lower()
        vis_status_var = globals()[f"{molecule_name_lower}_vis"]
        line_var = globals()[f"{molecule_name_lower}_line"]
        # lambdas_var = globals()[f"lambdas_{molecule_name_lower}"]
        # fluxes_var = globals()[f"fluxes_{molecule_name_lower}"]

        if vis_status_var:
            line_var.set_visible(True)
        else:
            line_var.set_visible(False)
            label = line_var.get_label()
            if label:
                ax1.legend().get_legend_handler_map().pop(label, None)
                line_var.set_label("_nolegend_")

    ax1.legend()

    # Creating an array that contains the data of every line in the water model and reseting the index of this array
    # Reference: "ir_model" > "intensity.py"
    # int_pars is used to call up information on water lines like when using the spanning feature of the tool
    int_pars = eval(f"{spanmol}_intensity.get_table")
    int_pars.index = range(len(int_pars.index))

    # Storing the callback for on_xlims_change()
    ax1.callbacks.connect('xlim_changed', on_xlims_change)

    # Storing the callback for the span selector
    span = SpanSelector(
        ax1,
        onselect,
        "horizontal",
        useblit=False,
        props=dict(alpha=0.5, facecolor="lime"),
        interactive=True,
        drag_from_anywhere=True
    )

    # Rebuilding the population diagram graph
    # See pop_diagram()
    pop_diagram()
    plt.draw(), canvas.draw()

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
"""
single_finder() is connected to the "Find Singles" button.
This function is a filter that finds molecular lines in the model that are isolated then prints vertical lines in the top graph where these lines are located
e.g. they are either a set distance away from other strong lines, or the intensity of the lines near the line are negligible.
"""


def single_finder():
    update()
    global fig_height
    global fig_bottom_height
    counter = 0
    specsep = float(specsep_entry.get())

    # Resetting the text feed box
    data_field.delete('1.0', "end")

    # Getting all the water lines in the range of xp1 and xp2
    int_pars_line = int_pars[(int_pars['lam'] > xp1) & (int_pars['lam'] < xp2)]
    int_pars_line.index = range(len(int_pars_line.index))

    # Parsing the wavelengths and intensities of the lines in int_pars_line
    lamb_cnts = int_pars_line['lam']
    intensities = int_pars_line['intens']

    # Determining an max threshold for lines we may want to consider
    # This threshold is based on the max line intensity found in the range of xp1 and xp2
    # This threshold will be used to filter out weak lines regardless of them being single
    max_intens = 0
    for i in range(len(intensities)):
        if intensities[i] > max_intens:
            max_intens = intensities[i]
    max_threshold = max_intens * line_threshold  # This will be used to filter out lines with intensities below a percentage of the max intensity

    # This is the main function. First, it will only consider lines with intensities above "max_threshold."
    # Of those lines, it will inspect all lines within "specsep" (user defined) below and above their wavelength.
    # If any lines within this range have an intensity above "threshold" (a percentage of the intensity for the line of interest),
    # then the line of interest is determined to be non-single. Otherwise, it's determined to be single.
    for j in int_pars_line.index:
        include = True  # Boolean for determining line is single or not.
        j_lam = lamb_cnts[int_pars_line.index[j]]  # Wavelength of line of interest
        sub_xmin = j_lam - specsep
        sub_xmax = j_lam + specsep
        j_intens = intensities[int_pars_line.index[j]]  # Intensity of line of interest
        loc_threshold = j_intens * 0.1  # Creating a threshold for determining locally if line of interest is single
        if j_intens >= max_threshold:  # Filter out weak lines
            chk_range = int_pars[(int_pars['lam'] > sub_xmin) & (int_pars['lam'] < sub_xmax)]
            chk_range.index = range(len(chk_range.index))
            range_intens = chk_range[
                'intens']  # Intensities of lines +/- "specsep" wavelength away from line of interest
            for k in chk_range.index:
                k_intens = range_intens[chk_range.index[k]]
                if k_intens >= loc_threshold:  # Filter determining if line of interest is not single
                    if k_intens != j_intens:  # Making sure we are not excluding line of interest by accidently considering its own intensity for the filter
                        include = False  # If both filters above are true, then the line of interest is not single
            if include == True:  # If both filters above are false for all lines in range of "specsep", then line of interest is single
                ax1.vlines(lamb_cnts[int_pars_line.index[j]], fig_bottom_height, fig_height, linestyles='dashed',
                           color='blue')
                counter = counter + 1

    # Storing the callback for on_xlims_change()
    ax1.callbacks.connect('xlim_changed', on_xlims_change)

    # Print the number of isolated lines that the function found in the region of xp1 and xp2
    if counter == 0:
        data_field.insert('1.0', 'No single lines found in the current wavelength range.')
    if counter > 0:
        data_field.insert('1.0',
                          'There are ' + str(counter) + ' single lines found in the current wavelength range.')
    canvas.draw()

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
def plot_spectrum_around_line(lamb, xmin, xmax):
    global wave_data, flux_data, lamb_cnts, intensities, einstein, e_up, up_lev, low_lev, g_up, tau, max_intensity, max_y, spanmol

    int_pars = eval(f"{spanmol}_intensity.get_table")
    int_pars.index = range(len(int_pars.index))

    # Getting all the water lines for the selected range
    int_pars_line = int_pars[(int_pars['lam'] > xmin) & (int_pars['lam'] < xmax)]
    int_pars_line.index = range(len(int_pars_line.index))

    # Parsing out the columns of the lines in int_pars_line to be used later
    lamb_cnts = int_pars_line['lam']
    intensities = int_pars_line['intens']
    einstein = int_pars_line['a_stein']
    e_up = int_pars_line['e_up']
    up_lev = int_pars_line['lev_up']
    low_lev = int_pars_line['lev_low']
    g_up = int_pars_line['g_up']
    tau = int_pars_line['tau']

    # Creating zero variables to be used later
    max_value = intensities[0]
    max_index = 0

    # Checking to see if there are any lines in the range selected
    # If there aren't then this function does not continue
    # If there are, then the strongest intensity of the lines in the range selected is identified along with its index
    if len(intensities) >= 1:
        selectedline = True
        for i in range(len(intensities)):
            if intensities[i] > max_value:
                max_value = intensities[i]
                max_index = i
    else:
        return

    # Defining the other parameters of the line with the strongest intensity as found previously
    max_lamb_cnts = lamb_cnts[max_index]
    max_up_lev = up_lev[max_index]
    max_low_lev = low_lev[max_index]
    max_intensity = intensities[max_index]
    max_einstein = einstein[max_index]
    max_e_up = e_up[max_index]
    max_g_up = g_up[max_index]
    max_tau = tau[max_index]

    # Finding the index of the minimum and maximum flux for both the data and model to be used in scaling the zoom graph (section below)
    model_indmin, model_indmax = np.searchsorted(lambdas_h2o, (xmin, xmax))
    data_indmin, data_indmax = np.searchsorted(wave_data, (xmin, xmax))
    # this below is to avoid taking too few pixels for the plot, useful in case of e.g. MIRI spectra
    data_indmin = data_indmin - 1
    data_indmax = data_indmax + 1
    model_indmax = min(len(lambdas_h2o) - 1, model_indmax)
    data_indmax = min(len(wave_data) - 1, data_indmax)

    # Dynamically set the x variable
    model_region_x_str = f"lambdas_{spanmol}[model_indmin:model_indmax]"
    model_region_x = eval(model_region_x_str)

    # Scaling the zoom graph
    # First, it's determined if the max intensity of the model is bigger than that of the max intensity of the data or vice versa
    # Then, the max for the y-axis is determined by the max intensity of either the model or data, whichever is bigger
    # The minimum for the y-axis of the zoom graph is set to zero here

    # model_region_y = fluxes_h2o[model_indmin:model_indmax]
    # Dynamically set the variable
    model_region_y_str = f"fluxes_{spanmol}[model_indmin:model_indmax]"
    model_region_y = eval(model_region_y_str)
    data_region_x = wave_data[data_indmin:data_indmax]
    data_region_y = flux_data[data_indmin:data_indmax]
    max_data_y = np.nanmax(data_region_y)
    max_model_y = np.nanmax(model_region_y)
    if (max_model_y) >= (max_data_y):
        max_y = max_model_y
    else:
        max_y = max_data_y
    ax2.set_ylim(0, max_y)

    # Define a small range around the selected wavelength
    padding = 0.1  # Fixed padding as per your request
    xmin_new = lamb - padding
    xmax_new = lamb + padding

    # Find the indices corresponding to this range in wave_data
    data_indmin, data_indmax = np.searchsorted(wave_data, (xmin_new, xmax_new))

    ax2.clear()

    # Extract and plot the observed data within the new range
    data_region_x = wave_data[data_indmin:data_indmax]
    data_region_y = flux_data[data_indmin:data_indmax]
    ax2.plot(data_region_x, data_region_y, color='black', label='Observed Data')

    # Extract and plot the model data within the new range
    # (Assuming model data is stored in similar arrays as wave_data and flux_data)
    model_region_x = wave_data[data_indmin:data_indmax]  # Replace with model x-data if available
    model_region_y = flux_data[data_indmin:data_indmax]  # Replace with model y-data if available
    ax2.plot(model_region_x, model_region_y, color='red', linestyle='--', label='Model Data')

    # Plot vertical lines for each line in the selected range
    for i in range(len(lamb_cnts)):
        if xmin_new <= lamb_cnts[i] <= xmax_new:
            lineheight = (intensities[i] / max_intensity) * max_y
            ax2.vlines(lamb_cnts[i], 0, lineheight, linestyles='dashed', color='green')
            ax2.text(lamb_cnts[i], lineheight, f'{e_up[i]:.0f}, {einstein[i]:.3f}', color='green', fontsize='small')

    # Highlight the selected line in orange
    lineheight = (max_intensity / max_intensity) * max_y  # Full height for selected line
    ax2.vlines(lamb, 0, lineheight, linestyles='dashed', color='orange')
    ax2.text(lamb, lineheight, f'{e_up[i]:.0f}, {einstein[i]:.3f}', color='orange', fontsize='small')

    # Set axes labels and title
    ax2.set_xlim(xmin_new, xmax_new)
    ax2.set_xlabel('Wavelength (μm)')
    ax2.set_ylabel('Flux density (Jy)')
    ax2.set_title(f'Spectrum around {lamb:.4f} μm', fontsize='medium')
    ax2.grid(False)

    # Redraw the canvas to update the plot
    canvas.draw()

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def onpick3(event):
        global default_line, line2save, intensities, lamb_cnts

        # Check if the clicked artist is a line in ax2 or a scatter point in ax3
        if event.artist in green_lines or event.artist in green_scatter:
            idx = green_lines.index(event.artist) if event.artist in green_lines else green_scatter.index(
                event.artist)  # Get the index of the clicked line
            lam = lamb_cnts[idx]  # Wavelength of the selected line
            lineheight = (intensities[idx] / max_intensity) * max_y  # Height of the selected line

            # Reset the previous default strongest line
            if default_line is not None:
                # Reset the color and style of the previous default line

                prev_scatter = default_line[5]  # Get the previous scatter point
                prev_scatter.set_color('green')  # Reset scatter point color to green
                prev_scatter.set_edgecolors('black')  # Reset scatter edge color to black

            # Find the corresponding scatter point for this line
            scatter = green_scatter[idx]
            scatter.set_color('orange')  # Change the color of the scatter point to orange
            scatter.set_edgecolors('black')  # Optional: change the edge color

            # Update default_line
            default_line = (idx, lamb_cnts[idx], lineheight, e_up[idx], einstein[idx], scatter)

            # Update the line2save DataFrame
            try:
                line2save = {
                    'species': [spanmol.upper()],
                    'lev_up': [up_lev[idx]],
                    'lev_low': [low_lev[idx]],
                    'lam': [lamb_cnts[idx]],
                    'tau': [tau[idx]],
                    'intens': [intensities[idx]],
                    'a_stein': [einstein[idx]],
                    'e_up': [e_up[idx]],
                    'g_up': [g_up[idx]],
                    'xmin': [f'{xmin:.{4}f}'],
                    'xmax': [f'{xmax:.{4}f}']
                }
                line2save = pd.DataFrame(line2save)
            except KeyError as e:
                pass  # Silencing the KeyError, so it doesn't affect functionality

            # Update the data field with the selected line's details
            try:
                line_flux = flux_integral(lam=wave_data, flux=flux_data, lam_min=xmin, lam_max=xmax, err=err_data)
                data_field.delete('1.0', "end")
                data_field.insert('1.0', (
                        'Strongest line:' + '\nUpper level = ' + str(up_lev[idx]) +
                        '\nLower level = ' + str(low_lev[idx]) +
                        '\nWavelength (μm) = ' + str(lamb_cnts[idx]) +
                        '\nEinstein-A coeff. (1/s) = ' + str(einstein[idx]) +
                        '\nUpper level energy (K) = ' + str(f'{e_up[idx]:.{0}f}') +
                        '\nOpacity = ' + str(f'{tau[idx]:.{3}f}') +
                        '\nFlux in sel. range (erg/s/cm2) = ' + str(f'{line_flux[0]:.{3}e}')
                ))
            except KeyError as e:
                pass  # Silencing the KeyError, so it doesn't affect functionality

            fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', onpick3)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def print_atomic_lines():
    update()
    ax1.callbacks.connect('xlim_changed', on_xlims_change)

    svd_lns = pd.read_csv("../LINELISTS/Atomic_lines.csv", sep=',')
    svd_lamb = np.array(svd_lns['wave'])
    svd_species = svd_lns['species']
    svd_lineID = np.array(svd_lns['line'])

    for i in range(len(svd_lamb)):
        ax1.vlines(svd_lamb[i], -2, 2, linestyles='dashed', color='tomato')

        # Adjust the y-coordinate to place labels within the borders
        label_y = ax1.get_ylim()[1]

        # Adjust the x-coordinate to place labels just to the right of the line
        label_x = svd_lamb[i] + 0.006 * (ax1.get_xlim()[1] - ax1.get_xlim()[0])

        ax1.text(label_x, label_y, svd_species[i] + ' ' + svd_lineID[i] + ' ', fontsize=8, rotation=90, va='top',
                 ha='left', color='tomato')

    data_field.insert('1.0', 'Atomic lines retrieved from file.')

    canvas.draw()


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
"""
onselect() is the function for the span selector functionality in the top graph of the tool.
Here, the user selects a range in the top graph and the range of the data and water model spectrum are rebuilt in the zoom graph (bottom left graph) 
along with the water lines in that range.
The strongest line is determined and its info is printed in the text feed on the left. 
The lines are also highlighted in the population diagram graph in this function.
"""


def onselect(xmin, xmax):
    global onselect_lines, wave_data, flux_data, line2save, selectedline, spanmol, model_indmin, model_indmax, data_region_x, model_line_select, green_lines, green_scatter, default_line, current_selected_line, intensities, lamb_cnts, e_up, einstein, err_data

    xdif = xmax - xmin
    if xdif > 0:
        # Clearing the bottom two graphs
        ax3.clear()
        ax2.clear()

        int_pars = eval(f"{spanmol}_intensity.get_table")
        int_pars.index = range(len(int_pars.index))

        # Getting all the lines for the selected range
        int_pars_line = int_pars[(int_pars['lam'] > xmin) & (int_pars['lam'] < xmax)]

        # Clearing the text feed box.
        data_field.delete('1.0', "end")

        # Repopulating the population diagram graph with all the lines of the molecule (gray dots)
        pop_diagram()

        # Resetting the labels of graphs after they were deleted by the clear function above
        ax2.set_xlabel('Wavelength (μm)')
        ax2.set_ylabel('Flux density (Jy)')
        ax2.set_title('Line inspection plot', fontsize='medium')

        linevar = eval(f"{spanmol}_line")
        linecolor = linevar.get_color()

        # Make empty lines for the zoom plot
        model_line_select, = ax2.plot([], [], color=linecolor, linewidth=3, ls='--')
        data_line_select, = ax2.plot([], [], color=foreground, linewidth=1)

        if len(int_pars_line) != 0:
            int_pars_line.index = range(len(int_pars_line.index))

            # Parsing out the columns of the lines in int_pars_line to be used later
            lamb_cnts = int_pars_line['lam']
            intensities = int_pars_line['intens']
            einstein = int_pars_line['a_stein']
            e_up = int_pars_line['e_up']
            up_lev = int_pars_line['lev_up']
            low_lev = int_pars_line['lev_low']
            g_up = int_pars_line['g_up']
            tau = int_pars_line['tau']

            # Creating zero variables to be used later
            max_value = intensities[0]
            max_index = 0

            # Checking to see if there are any lines in the range selected
            if len(intensities) >= 1:
                selectedline = True
                for i in range(len(intensities)):
                    if intensities[i] > max_value:
                        max_value = intensities[i]
                        max_index = i
            else:
                return

            # Defining the other parameters of the line with the strongest intensity
            max_lamb_cnts = lamb_cnts[max_index]
            max_up_lev = up_lev[max_index]
            max_low_lev = low_lev[max_index]
            max_intensity = intensities[max_index]
            max_einstein = einstein[max_index]
            max_e_up = e_up[max_index]
            max_g_up = g_up[max_index]
            max_tau = tau[max_index]

            onselect_lines = int_pars_line.loc[(int_pars_line['intens'] > max_intensity / 50)]

            # Finding the index of the minimum and maximum flux for both the data and model
            model_indmin, model_indmax = np.searchsorted(lambdas_h2o, (xmin, xmax))
            data_indmin, data_indmax = np.searchsorted(wave_data, (xmin, xmax))
            data_indmin = data_indmin - 1
            data_indmax = data_indmax + 1
            model_indmax = min(len(lambdas_h2o) - 1, model_indmax)
            data_indmax = min(len(wave_data) - 1, data_indmax)

            # Dynamically set the x variable
            model_region_x_str = f"lambdas_{spanmol}[model_indmin:model_indmax]"
            model_region_x = eval(model_region_x_str)

            # Scaling the zoom graph
            model_region_y_str = f"fluxes_{spanmol}[model_indmin:model_indmax]"
            model_region_y = eval(model_region_y_str)
            data_region_x = wave_data[data_indmin:data_indmax]
            data_region_y = flux_data[data_indmin:data_indmax]
            max_data_y = np.nanmax(data_region_y)
            max_model_y = np.nanmax(model_region_y)
            max_y = max(max_model_y, max_data_y)
            ax2.set_ylim(0, max_y)

            # Calling the flux function to calculate the flux for the data in the range selected
            line_flux = flux_integral(lam=wave_data, flux=flux_data, lam_min=xmin, lam_max=xmax, err=err_data)

            data_field.delete('1.0', "end")
            data_field.insert('1.0', (
                    'Strongest line:' + '\nUpper level = ' + str(max_up_lev) +
                    '\nLower level = ' + str(max_low_lev) +
                    '\nWavelength (μm) = ' + str(max_lamb_cnts) +
                    '\nEinstein-A coeff. (1/s) = ' + str(max_einstein) +
                    '\nUpper level energy (K) = ' + str(f'{max_e_up:.{0}f}') +
                    '\nOpacity = ' + str(f'{max_tau:.{3}f}') +
                    '\nFlux in sel. range (erg/s/cm2) = ' + str(f'{line_flux[0]:.{3}e}')
            ))

            # Creating a pandas dataframe for all the info of the strongest line in the selected range
            line2save = {
                'species': [spanmol.upper()],
                'lev_up': [max_up_lev],
                'lev_low': [max_low_lev],
                'lam': [max_lamb_cnts],
                'tau': [max_tau],
                'intens': [max_intensity],
                'a_stein': [max_einstein],
                'e_up': [max_e_up],
                'g_up': [max_g_up],
                'xmin': [f'{xmin:.{4}f}'],
                'xmax': [f'{xmax:.{4}f}']
            }
            line2save = pd.DataFrame(line2save)

            default_line = None

            green_lines = []
            green_scatter = []

            # Plot the lines in the zoom range
            if len(model_region_x) >= 1:
                k = 0
                model_line_select.set_data(model_region_x, model_region_y)
                data_line_select.set_data(data_region_x, data_region_y)
                ax2.set_xlim(model_region_x[0], model_region_x[-1])

                for j in range(len(lamb_cnts)):
                    lineheight = (intensities[j] / max_intensity) * max_y
                    # if intensities[j] > max_intensity / 50:
                    line = ax2.vlines(lamb_cnts[j], 0, lineheight, linestyles='dashed', color='green',
                                      picker=True) if j != max_index else ax2.vlines(lamb_cnts[j], 0, lineheight,
                                                                                     linestyles='dashed',
                                                                                     color='orange',
                                                                                     picker=True)
                    green_lines.append(line)
                    text = ax2.text(lamb_cnts[j], lineheight,
                                    (str(f'{e_up[j]:.{0}f}') + ', ' + str(f'{einstein[j]:.{3}f}')), color='green',
                                    fontsize='small')
                    area = eval(f"np.pi*({spanmol}_radius*au*1e2)**2")  # In cm^2
                    Dist = dist * pc
                    beam_s = area / Dist ** 2
                    F = intensities[j] * beam_s
                    freq = ccum / lamb_cnts[j]
                    rd_yax = np.log(4 * np.pi * F / (einstein[j] * hh * freq * g_up[j]))
                    scatter = ax3.scatter(e_up[j], rd_yax, s=30, color='green', edgecolors='black',
                                          picker=True) if j != max_index else ax3.scatter(e_up[j], rd_yax, s=30,
                                                                                          color='orange',
                                                                                          edgecolors='black',
                                                                                          picker=True)
                    green_scatter.append(scatter)
                    # If the intensity is below the threshold, remove the line and scatter
                    threshold_intensity = max_intensity / 50
                    if intensities[j] < threshold_intensity:
                        green_lines[j].remove()
                        text.remove()
                        green_scatter[j].remove()
                    if j == max_index:
                        default_line = (j, lamb_cnts[j], lineheight, e_up[j], einstein[j], scatter)

                fig.canvas.flush_events()

                def onpick(event):
                    global default_line, line2save, intensities, lamb_cnts

                    # Check if the clicked artist is a line in ax2 or a scatter point in ax3
                    if event.artist in green_lines or event.artist in green_scatter:
                        idx = green_lines.index(event.artist) if event.artist in green_lines else green_scatter.index(
                            event.artist)  # Get the index of the clicked line

                        lineheight = (intensities[idx] / max_intensity) * max_y  # Height of the selected line

                        # Reset the previous default strongest line
                        if default_line is not None:
                            # Reset the color and style of the previous default line
                            prev_line = green_lines[default_line[0]]  # Get the previous line from green_lines
                            prev_line.set_color('green')  # Reset color to green
                            prev_line.set_linewidth(1)  # Reset line width (if needed)

                            prev_scatter = default_line[5]  # Get the previous scatter point
                            prev_scatter.set_color('green')  # Reset scatter point color to green
                            prev_scatter.set_edgecolors('black')  # Reset scatter edge color to black

                        # Highlight the selected line
                        selected_line = green_lines[idx]  # Get the existing line
                        selected_line.set_color('orange')  # Change the color to orange
                        selected_line.set_linewidth(2)  # Optionally increase line width for highlight

                        # Find the corresponding scatter point for this line
                        scatter = green_scatter[idx]
                        scatter.set_color('orange')  # Change the color of the scatter point to orange
                        scatter.set_edgecolors('black')  # Optional: change the edge color

                        # Update default_line
                        default_line = (idx, lamb_cnts[idx], lineheight, e_up[idx], einstein[idx], scatter)

                        # Update the line2save DataFrame
                        try:
                            line2save = {
                                'species': [spanmol.upper()],
                                'lev_up': [up_lev[idx]],
                                'lev_low': [low_lev[idx]],
                                'lam': [lamb_cnts[idx]],
                                'tau': [tau[idx]],
                                'intens': [intensities[idx]],
                                'a_stein': [einstein[idx]],
                                'e_up': [e_up[idx]],
                                'g_up': [g_up[idx]],
                                'xmin': [f'{xmin:.{4}f}'],
                                'xmax': [f'{xmax:.{4}f}']
                            }
                            line2save = pd.DataFrame(line2save)

                            # Update the data field with the selected line's details

                            flux_integral(lam=wave_data, flux=flux_data, lam_min=xmin, lam_max=xmax, err=err_data)
                            data_field.delete('1.0', "end")
                            data_field.insert('1.0', (
                                    'Strongest line:' + '\nUpper level = ' + str(up_lev[idx]) +
                                    '\nLower level = ' + str(low_lev[idx]) +
                                    '\nWavelength (μm) = ' + str(lamb_cnts[idx]) +
                                    '\nEinstein-A coeff. (1/s) = ' + str(einstein[idx]) +
                                    '\nUpper level energy (K) = ' + str(f'{e_up[idx]:.{0}f}') +
                                    '\nOpacity = ' + str(f'{tau[idx]:.{3}f}') +
                                    '\nFlux in sel. range (erg/s/cm2) = ' + str(f'{line_flux[0]:.{3}e}')
                            ))
                        except KeyError as e:
                            pass  # Silencing the KeyError, so it doesn't affect functionality

                        fig.canvas.draw()

                fig.canvas.mpl_connect('pick_event', onpick)
        else:
            data_field.delete('1.0', "end")
            data_field.insert('1.0', 'No lines in selected range, please select another molecule from the menu.')
    else:
        pop_diagram()
        ax2.clear()


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
        
"""
submit_col() is connected to the text input box for adjusting the 
column density of the currently selected molecule
"""


def submit_col(event, text):
    # global text_box
    # global text_box_data

    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Submitting Density...')
    plt.draw(), canvas.draw()
    fig.canvas.flush_events()

    val = float(event)
    exec(f"n_mol_{text} = {val}", globals())

    # Intensity calculation
    exec(f"{text}_intensity.calc_intensity(t_{text}, n_mol_{text}, dv=intrinsic_line_width)", globals())

    # Spectrum creation
    exec(
        f"{text}_spectrum = Spectrum(lam_min=min_lamb, lam_max=max_lamb, dlambda=model_pixel_res, R=model_line_width, distance=dist)",
        globals())

    # Adding intensity to the spectrum
    exec(f"{text}_spectrum.add_intensity({text}_intensity, {text}_radius ** 2 * np.pi)", globals())

    # Fluxes and lambdas
    exec(f"fluxes_{text} = {text}_spectrum.flux_jy; lambdas_{text} = {text}_spectrum.lamgrid", globals())

    # Dynamically set the data for each molecule's line using exec and globals()
    exec(f"{text}_line.set_data(lambdas_{text}, fluxes_{text})", globals())

    # Clearing the text feed box.
    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Density Updated!')
    plt.draw(), canvas.draw()
    fig.canvas.flush_events()

    # plt.pause(3)

    # Clearing the text feed box.
    data_field.delete('1.0', "end")
    plt.draw(), canvas.draw()

    # Initialize total fluxes list
    total_fluxes = []
    # Calculate total fluxes based on visibility conditions
    for i in range(len(lambdas_h2o)):
        flux_sum = 0
        for mol_name, mol_filepath, mol_label in molecules_data:

            mol_name_lower = mol_name.lower()
            visibility_flag = f"{mol_name_lower}_vis"
            fluxes_molecule = f"fluxes_{mol_name_lower}"

            if visibility_flag in globals() and globals()[visibility_flag]:
                flux_sum += globals()[fluxes_molecule][i]

        total_fluxes.append(flux_sum)

    sum_line.set_data(lambdas_h2o, total_fluxes)
    write_user_csv(molecules_data)
    update()
    pop_diagram()
    canvas.draw()

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def submit_temp(event, text):
    # print(event)
    # global text_box
    # global text_box_data
    global xp1
    global xp2
    global span
    global model_line_select
    global data_line_select
    global fig_height
    global fig_bottom_height
    global n_mol
    global selectedline
    global int_pars
    global molecules_data
    global total_fluxes

    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Submitting Temperature...')
    plt.draw(), canvas.draw()
    fig.canvas.flush_events()

    val = float(event)
    exec(f"t_{text} = {val}", globals())

    # Intensity calculation
    exec(f"{text}_intensity.calc_intensity(t_{text}, n_mol_{text}, dv=intrinsic_line_width)", globals())

    # Spectrum creation
    exec(
        f"{text}_spectrum = Spectrum(lam_min=min_lamb, lam_max=max_lamb, dlambda=model_pixel_res, R=model_line_width, distance=dist)",
        globals())

    # Adding intensity to the spectrum
    exec(f"{text}_spectrum.add_intensity({text}_intensity, {text}_radius ** 2 * np.pi)", globals())

    # Fluxes and lambdas
    exec(f"fluxes_{text} = {text}_spectrum.flux_jy; lambdas_{text} = {text}_spectrum.lamgrid", globals())

    # Dynamically set the data for each molecule's line using exec and globals()
    exec(f"{text}_line.set_data(lambdas_{text}, fluxes_{text})", globals())

    # Clearing the text feed box.
    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Temperature Updated!')
    plt.draw(), canvas.draw()
    fig.canvas.flush_events()

    # plt.pause(3)

    # Clearing the text feed box.
    data_field.delete('1.0', "end")
    plt.draw(), canvas.draw()

    # sum_line, = ax1.plot([], [], color='gray', linewidth=1)
    # sum_line.set_label('Sum')
    # ax1.legend()

    # Initialize total fluxes list
    total_fluxes = []
    # Calculate total fluxes based on visibility conditions
    for i in range(len(lambdas_h2o)):
        flux_sum = 0
        for mol_name, mol_filepath, mol_label in molecules_data:

            mol_name_lower = mol_name.lower()
            visibility_flag = f"{mol_name_lower}_vis"
            fluxes_molecule = f"fluxes_{mol_name_lower}"

            if visibility_flag in globals() and globals()[visibility_flag]:
                flux_sum += globals()[fluxes_molecule][i]

        total_fluxes.append(flux_sum)

    sum_line.set_data(lambdas_h2o, total_fluxes)
    # exec(sum_line.set_data(lambdas_h2o, total_fluxes), globals())
    write_user_csv(molecules_data)
    update()
    pop_diagram()
    plt.draw(), canvas.draw()
    fig.canvas.flush_events()

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def submit_rad(event, text):
    # global text_box
    # global text_box_data

    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Submitting Radius...')
    plt.draw(), canvas.draw()
    fig.canvas.flush_events()

    val = float(event)
    exec(f"{text}_radius = {val}", globals())

    # Intensity calculation
    exec(f"{text}_intensity.calc_intensity(t_{text}, n_mol_{text}, dv=intrinsic_line_width)", globals())

    # Spectrum creation
    exec(
        f"{text}_spectrum = Spectrum(lam_min=min_lamb, lam_max=max_lamb, dlambda=model_pixel_res, R=model_line_width, distance=dist)",
        globals())

    # Adding intensity to the spectrum
    exec(f"{text}_spectrum.add_intensity({text}_intensity, {text}_radius ** 2 * np.pi)", globals())

    # Fluxes and lambdas
    exec(f"fluxes_{text} = {text}_spectrum.flux_jy; lambdas_{text} = {text}_spectrum.lamgrid", globals())

    # Dynamically set the data for each molecule's line using exec and globals()
    exec(f"{text}_line.set_data(lambdas_{text}, fluxes_{text})", globals())

    # Clearing the text feed box.
    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Radius updated!')
    plt.draw(), canvas.draw()
    fig.canvas.flush_events()

    # Clearing the text feed box.
    data_field.delete('1.0', "end")
    plt.draw(), canvas.draw()

    # Initialize total fluxes list
    total_fluxes = []
    # Calculate total fluxes based on visibility conditions
    for i in range(len(lambdas_h2o)):
        flux_sum = 0
        for mol_name, mol_filepath, mol_label in molecules_data:

            mol_name_lower = mol_name.lower()
            visibility_flag = f"{mol_name_lower}_vis"
            fluxes_molecule = f"fluxes_{mol_name_lower}"

            if visibility_flag in globals() and globals()[visibility_flag]:
                flux_sum += globals()[fluxes_molecule][i]

        total_fluxes.append(flux_sum)

    sum_line.set_data(lambdas_h2o, total_fluxes)
    write_user_csv(molecules_data)
    update()
    pop_diagram()
    canvas.draw()


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
        
def load_variables_from_file(file_name):
    # global text_box_data
    # global text_box
    global molecules_data, nextrow
    # Display a confirmation dialog
    confirmed = tk.messagebox.askquestion("Confirmation",
                                          "Sure you want to load parameters? Make sure to save any unsaved changes!")
    if confirmed == "no":  # Check if user clicked "no"
        return
    if not os.path.exists(os.path.join(save_folder, f"{file_name}-molsave.csv")):
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'No save for data file found.')
        return

    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Loading saved parameters, this may take a moment...')
    plt.draw(), canvas.draw()
    fig.canvas.flush_events()

    # del_molecule_data()

    molecules_data = read_from_csv()

    # Read molecules_list.csv
    molecules_list = []
    new_molecules = []
    missing_molecules = []  # Initialize the missing_molecules array
    try:
        with open(os.path.join(save_folder, "molecules_list.csv"), 'r') as list_file:
            reader = csv.reader(list_file)
            next(reader)  # Skip header
            for row in reader:
                molecules_list.append(tuple(row[:3]))  # Taking the first three columns of each row
    except Exception as e:
        print("Error reading molecules_list.csv:", e)

    # Create a set of molecule names from molecules_data
    molecules_data_names = set(item[0] for item in molecules_data)

    # Create a set of molecule names from molecules_data
    molecules_list_names = set(item[0] for item in molecules_list)

    # Append missing molecules from molecules_list.csv
    for mol_name, mol_path, mol_label in molecules_data:
        if mol_name not in molecules_list_names:
            new_molecules.append((mol_name, mol_path, mol_label))

    # Append missing molecules from molecules_list.csv
    for mol_name, mol_path, mol_label in molecules_list:
        if mol_name not in molecules_data_names:
            missing_molecules.append((mol_name, mol_path, mol_label))  # Add to missing_molecules
            molecules_data.append((mol_name, mol_path, mol_label))

    print(f"new molecules:{new_molecules}")

    # Create labels for columns
    for col, label in enumerate(column_labels):
        label_widget = tk.Label(molecule_frame, text=label)
        label_widget.grid(row=0, column=col)

    # Loop to create rows of input fields and buttons for each chemical
    # nextrow = 1  # Start with row 1
    for row, (mol_name, mol_filepath, mol_label) in enumerate(new_molecules):
        # global nextrow
        y_row = start_y + row_height * (num_rows - row - 1)
        row = nextrow
        # Get the initial values for the current chemical from the dictionary
        params = initial_parameters.get(mol_name, default_initial_params)
        scale_exponent = params["scale_exponent"]
        scale_number = params["scale_number"]
        t_kin = params["t_kin"]
        radius_init = params["radius_init"]

        # Calculate and set n_mol_init for the current molecule
        n_mol_init = float(scale_number * (10 ** scale_exponent))

        # Import line lists from the ir_model folder
        mol_data = MolData(mol_name, mol_filepath)

        # Use exec() to create the variables with specific variable names for each molecule
        exec(f"mol_{mol_name.lower()} = MolData('{mol_name}', '{mol_filepath}')", globals())

        # Row label
        exec(f"{mol_name.lower()}_rowl_field = tk.Entry(molecule_frame, width=6)", globals())
        eval(f"{mol_name.lower()}_rowl_field").grid(row=row, column=0)
        eval(f"{mol_name.lower()}_rowl_field").insert(0, f"{mol_name}")
        # molecule_elements[mol_name.lower()] = {'rowl': mol_name.lower() + '_rowl_field'}

        # Temperature input field
        globals()[f"{mol_name.lower()}_temp_field"] = tk.Entry(molecule_frame, width=4)

        eval(f"{mol_name.lower()}_temp_field").grid(row=row, column=1)
        eval(f"{mol_name.lower()}_temp_field").insert(0, f"{t_kin}")
        # globals() [f"{mol_name.lower()}_submit_temp_button"] = tk.Button(window, text="Submit", command=lambda mn=mol_name.lower(), te = globals()[f"{mol_name.lower()}_temp_field"]: submit_temp(te.get(), mn))
        # eval(f"{mol_name.lower()}_submit_temp_button").grid(row=row + 1, column=2)
        # molecule_elements[mol_name.lower()] = {'temp': mol_name.lower() + '_temp_field'}
        eval(f"{mol_name.lower()}_temp_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
            f"{mol_name.lower()}_temp_field"]: submit_temp(ce.get(), mn))
        exec(f"t_{mol_name.lower()} = {t_kin}", globals())

        # Radius input field
        globals()[f"{mol_name.lower()}_rad_field"] = tk.Entry(molecule_frame, width=4)
        eval(f"{mol_name.lower()}_rad_field").grid(row=row, column=2)
        eval(f"{mol_name.lower()}_rad_field").insert(0, f"{radius_init}")
        # globals() [f"{mol_name.lower()}_submit_rad_button"] = tk.Button(window, text="Submit", command=lambda mn=mol_name.lower(), re = globals()[f"{mol_name.lower()}_rad_field"]: submit_rad(re.get(), mn))
        # eval(f"{mol_name.lower()}_submit_rad_button").grid(row=row + 1, column=4)
        # molecule_elements[mol_name.lower()]['rad'] = mol_name.lower() + '_rad_field'
        eval(f"{mol_name.lower()}_rad_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
            f"{mol_name.lower()}_rad_field"]: submit_rad(ce.get(), mn))
        exec(f"{mol_name.lower()}_radius = {radius_init}", globals())

        # Column Density input field
        globals()[f"{mol_name.lower()}_dens_field"] = tk.Entry(molecule_frame, width=6)
        eval(f"{mol_name.lower()}_dens_field").grid(row=row, column=3)
        eval(f"{mol_name.lower()}_dens_field").insert(0, f"{n_mol_init:.{1}e}")
        # globals() [f"{mol_name.lower()}_submit_col_button"] = tk.Button(window, text="Submit", command=lambda mn=mol_name.lower(), ce = globals()[f"{mol_name.lower()}_dens_field"]: submit_col(ce.get(), mn))
        # eval(f"{mol_name.lower()}_submit_col_button").grid(row=row + 1, column=6)
        # molecule_elements[mol_name.lower()]['dens'] = mol_name.lower() + '_dens_field'
        eval(f"{mol_name.lower()}_dens_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
            f"{mol_name.lower()}_dens_field"]: submit_col(ce.get(), mn))
        exec(f"n_mol_{mol_name.lower()} = {n_mol_init}", globals())

        # Visibility Checkbutton
        if mol_name.lower() == 'h2o':
            exec(f"{mol_name.lower()}_vis_status = tk.BooleanVar()")
            exec(f"{mol_name.lower()}_vis_status.set(True)")  # Set the initial state
            exec(
                f"{mol_name.lower()}_vis_checkbutton = tk.Checkbutton(molecule_frame, text='', variable={mol_name.lower()}_vis_status, onvalue=True, offvalue=False, command=lambda mn=mol_name.lower(): model_visible(mn))")
            exec(f"{mol_name.lower()}_vis_checkbutton.select()")
        else:
            globals()[f"{mol_name.lower()}_vis_status"] = tk.BooleanVar()
            globals()[f"{mol_name.lower()}_vis_checkbutton"] = tk.Checkbutton(molecule_frame, text='',
                                                                              variable=eval(
                                                                                  f"{mol_name.lower()}_vis_status"),
                                                                              command=lambda
                                                                                  mn=mol_name.lower(): model_visible(
                                                                                  mn))
            globals()[f"{mol_name.lower()}_vis_status"].set(False)  # Set the initial state

        globals()[f"{mol_name}_vis"] = False
        eval(f"{mol_name.lower()}_vis_checkbutton").grid(row=row, column=4)

        # Delete button
        del_button = tk.Button(molecule_frame, text="X",
                               command=lambda widget=eval(f"{mol_name.lower()}_rowl_field"): delete_row(widget))
        del_button.grid(row=row, column=5)

        color_button = tk.Button(molecule_frame, text=" ",
                                 command=lambda widget=eval(f"{mol_name.lower()}_rowl_field"): choose_color(widget))
        color_button.grid(row=row, column=6)

        exec(f"{mol_name.lower()}_line, = ax1.plot([], [], alpha=0.8, linewidth=1)", globals())
        exec(f"{mol_name.lower()}_line.set_label('{mol_name}')", globals())

        # Intensity calculation
        exec(f"{mol_name.lower()}_intensity = Intensity(mol_{mol_name.lower()})", globals())
        exec(
            f"{mol_name.lower()}_intensity.calc_intensity(t_{mol_name.lower()}, n_mol_{mol_name.lower()}, dv=intrinsic_line_width)",
            globals())
        # print(f"{mol_name.lower()}_intensity")
        # Add the variables to the globals dictionary
        globals()[f"{mol_name.lower()}_intensity"] = eval(f"{mol_name.lower()}_intensity")

        # Spectrum creation
        exec(
            f"{mol_name.lower()}_spectrum = Spectrum(lam_min=min_lamb, lam_max=max_lamb, dlambda=model_pixel_res, R=model_line_width, distance=dist)",
            globals())

        # Adding intensity to the spectrum
        exec(
            f"{mol_name.lower()}_spectrum.add_intensity({mol_name.lower()}_intensity, {mol_name.lower()}_radius ** 2 * np.pi)",
            globals())

        # Fluxes and lambdas
        exec(
            f"fluxes_{mol_name.lower()} = {mol_name.lower()}_spectrum.flux_jy; lambdas_{mol_name.lower()} = {mol_name.lower()}_spectrum.lamgrid",
            globals())

        # delete_button = tk.Button(molecule_frame, text="Delete", command=lambda r=row, mn=mol_name: delete_row(r, mn))
        # delete_button.grid(row=row, column=5)

        nextrow = nextrow + 1

    filename = os.path.join(save_folder, f"{file_name}-molsave.csv")
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)  # Read the header row
                rows = list(reader)  # Read all rows into a list
                for i, row in enumerate(rows):
                    mol_name, mol_filepath, mol_label, temp, rad, n_mol, color, vis, dist, stellarrv, fwhm, ilw = row
                    # Update global variables or GUI fields with the loaded values
                    exec(f"global t_{mol_name.lower()}; t_{mol_name.lower()} = {temp}")
                    exec(f"global {mol_name.lower()}_radius; {mol_name.lower()}_radius = {rad}")
                    exec(f"global n_mol_{mol_name.lower()}; n_mol_{mol_name.lower()} = {n_mol}")
                    exec(f"global {mol_name.lower()}_line_color; {mol_name.lower()}_line_color = '{color}'")
                    exec(f"global {mol_name.lower()}_color; {mol_name.lower()}_color = '{color}'")

                    exec(f"global {mol_name.lower()}_vis; {mol_name.lower()}_vis = {vis}")
                    exec(f"global dist; dist = {dist}")
                    exec(f"global star_rv; star_rv = {stellarrv}")
                    exec(f"global fwhm; fwhm = {fwhm}")
                    exec(f"global intrinsic_line_width; intrinsic_line_width = {ilw}")

                    # Update GUI fields
                    eval(f"{mol_name.lower()}_temp_field").delete(0, "end")
                    eval(f"{mol_name.lower()}_temp_field").insert(0, temp)

                    eval(f"{mol_name.lower()}_rad_field").delete(0, "end")
                    eval(f"{mol_name.lower()}_rad_field").insert(0, rad)

                    eval(f"{mol_name.lower()}_dens_field").delete(0, "end")
                    eval(f"{mol_name.lower()}_dens_field").insert(0, f"{float(n_mol):.{1}e}")

                    dist_entry.delete(0, "end")
                    dist_entry.insert(0, f"{dist}")

                    star_rv_entry.delete(0, "end")
                    star_rv_entry.insert(0, f"{star_rv}")

                    fwhm_entry.delete(0, "end")
                    fwhm_entry.insert(0, f"{fwhm}")

                    intrinsic_line_width_entry.delete(0, "end")
                    intrinsic_line_width_entry.insert(0, f"{intrinsic_line_width}")

                    # Call update_initvals() only on the last iteration
                    if i == len(rows) - 1:
                        update_initvals()

            # update()
            spanoptionsvar = [m[0] for m in molecules_data]
            spandropd['values'] = spanoptionsvar
            if spanoptionsvar:
                spandropd.set(spanoptionsvar[0])

            print("Variables loaded from CSV file.")
        except Exception as e:
            print("Error loading variables from CSV:", e)

    for row, (mol_name, _, _) in enumerate(molecules_data, start=1):

        linecolor = eval(f"{mol_name.lower()}_color")
        exec(f"{mol_name.lower()}_line.set_color('{linecolor}')", globals())
        # Get the molecule name in lower case
        mol_name_lower = mol_name.lower()

        # Get the line object
        line_var = globals().get(f"{mol_name_lower}_line")

        # Check if the line object exists and has a color attribute
        if line_var and hasattr(line_var, 'get_color'):
            # Get the color of the line
            line_color = line_var.get_color()
            globals()[f"{mol_name.lower()}_color"] = line_color

            # Get the color button from the grid_slaves list
            color_button = molecule_frame.grid_slaves(row=row, column=6)[0]
            # Set the background color of the color button
            color_button.configure(bg=line_color)

        if eval(f"{mol_name.lower()}_vis"):
            exec(f"{mol_name.lower()}_vis_checkbutton.select()")

        if not eval(f"{mol_name.lower()}_vis"):
            exec(f"{mol_name.lower()}_vis_checkbutton.deselect()")

    else:
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'Saved parameters file not found.')

    update()
    write_user_csv(molecules_data)
    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Saved parameters loaded from file.')

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
def load_defaults_from_file():
    # global text_box_data
    # global text_box
    global molecules_data, nextrow

    confirmed = tk.messagebox.askquestion("Confirmation",
                                          "Sure you want to load the default molecules? This will erase all current parameters (save first if you wish to).")
    if confirmed == "no":  # Check if user clicked "no"
        return

    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Loading default molecules, this may take a moment...')
    plt.draw(), canvas.draw()
    fig.canvas.flush_events()

    del_molecule_data()

    molecules_data = read_default_csv()
    # print(molecules_data)
    # Create labels for columns
    for col, label in enumerate(column_labels):
        label_widget = tk.Label(molecule_frame, text=label)
        label_widget.grid(row=0, column=col)

    # Loop to create rows of input fields and buttons for each chemical
    nextrow = 1  # Start with row 1
    for row, (mol_name, mol_filepath, mol_label) in enumerate(molecules_data):
        # global nextrow
        y_row = start_y + row_height * (num_rows - row - 1)
        row = row + 1
        # Get the initial values for the current chemical from the dictionary
        params = initial_parameters.get(mol_name, default_initial_params)
        scale_exponent = params["scale_exponent"]
        scale_number = params["scale_number"]
        t_kin = params["t_kin"]
        radius_init = params["radius_init"]

        # Calculate and set n_mol_init for the current molecule
        n_mol_init = float(scale_number * (10 ** scale_exponent))

        # Import line lists from the ir_model folder
        mol_data = MolData(mol_name, mol_filepath)

        # Use exec() to create the variables with specific variable names for each molecule
        exec(f"mol_{mol_name.lower()} = MolData('{mol_name}', '{mol_filepath}')", globals())

        # Row label
        exec(f"{mol_name.lower()}_rowl_field = tk.Entry(molecule_frame, width=6)", globals())
        eval(f"{mol_name.lower()}_rowl_field").grid(row=row, column=0)
        eval(f"{mol_name.lower()}_rowl_field").insert(0, f"{mol_name}")
        # molecule_elements[mol_name.lower()] = {'rowl': mol_name.lower() + '_rowl_field'}

        # Temperature input field
        globals()[f"{mol_name.lower()}_temp_field"] = tk.Entry(molecule_frame, width=4)

        eval(f"{mol_name.lower()}_temp_field").grid(row=row, column=1)
        eval(f"{mol_name.lower()}_temp_field").insert(0, f"{t_kin}")
        # globals() [f"{mol_name.lower()}_submit_temp_button"] = tk.Button(window, text="Submit", command=lambda mn=mol_name.lower(), te = globals()[f"{mol_name.lower()}_temp_field"]: submit_temp(te.get(), mn))
        # eval(f"{mol_name.lower()}_submit_temp_button").grid(row=row + 1, column=2)
        # molecule_elements[mol_name.lower()] = {'temp': mol_name.lower() + '_temp_field'}
        eval(f"{mol_name.lower()}_temp_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
            f"{mol_name.lower()}_temp_field"]: submit_temp(ce.get(), mn))
        exec(f"t_{mol_name.lower()} = {t_kin}", globals())

        # Radius input field
        globals()[f"{mol_name.lower()}_rad_field"] = tk.Entry(molecule_frame, width=4)
        eval(f"{mol_name.lower()}_rad_field").grid(row=row, column=2)
        eval(f"{mol_name.lower()}_rad_field").insert(0, f"{radius_init}")
        # globals() [f"{mol_name.lower()}_submit_rad_button"] = tk.Button(window, text="Submit", command=lambda mn=mol_name.lower(), re = globals()[f"{mol_name.lower()}_rad_field"]: submit_rad(re.get(), mn))
        # eval(f"{mol_name.lower()}_submit_rad_button").grid(row=row + 1, column=4)
        # molecule_elements[mol_name.lower()]['rad'] = mol_name.lower() + '_rad_field'
        eval(f"{mol_name.lower()}_rad_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
            f"{mol_name.lower()}_rad_field"]: submit_rad(ce.get(), mn))
        exec(f"{mol_name.lower()}_radius = {radius_init}", globals())

        # Column Density input field
        globals()[f"{mol_name.lower()}_dens_field"] = tk.Entry(molecule_frame, width=6)
        eval(f"{mol_name.lower()}_dens_field").grid(row=row, column=3)
        eval(f"{mol_name.lower()}_dens_field").insert(0, f"{n_mol_init:.{1}e}")
        # globals() [f"{mol_name.lower()}_submit_col_button"] = tk.Button(window, text="Submit", command=lambda mn=mol_name.lower(), ce = globals()[f"{mol_name.lower()}_dens_field"]: submit_col(ce.get(), mn))
        # eval(f"{mol_name.lower()}_submit_col_button").grid(row=row + 1, column=6)
        # molecule_elements[mol_name.lower()]['dens'] = mol_name.lower() + '_dens_field'
        eval(f"{mol_name.lower()}_dens_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
            f"{mol_name.lower()}_dens_field"]: submit_col(ce.get(), mn))
        exec(f"n_mol_{mol_name.lower()} = {n_mol_init}", globals())

        # Visibility Checkbutton
        if mol_name.lower() == 'h2o':
            exec(f"{mol_name.lower()}_vis_status = tk.BooleanVar()")
            exec(f"{mol_name.lower()}_vis_status.set(True)")  # Set the initial state
            exec(
                f"{mol_name.lower()}_vis_checkbutton = tk.Checkbutton(molecule_frame, text='', variable={mol_name.lower()}_vis_status, onvalue=True, offvalue=False, command=lambda mn=mol_name.lower(): model_visible(mn))")
            exec(f"{mol_name.lower()}_vis_checkbutton.select()")
        else:
            globals()[f"{mol_name.lower()}_vis_status"] = tk.BooleanVar()
            globals()[f"{mol_name.lower()}_vis_checkbutton"] = tk.Checkbutton(molecule_frame, text='',
                                                                              variable=eval(
                                                                                  f"{mol_name.lower()}_vis_status"),
                                                                              command=lambda
                                                                                  mn=mol_name.lower(): model_visible(
                                                                                  mn))
            globals()[f"{mol_name.lower()}_vis_status"].set(False)  # Set the initial state

        globals()[f"{mol_name}_vis"] = False
        eval(f"{mol_name.lower()}_vis_checkbutton").grid(row=row, column=4)

        # Delete button
        del_button = tk.Button(molecule_frame, text="X",
                               command=lambda widget=eval(f"{mol_name.lower()}_rowl_field"): delete_row(widget))
        del_button.grid(row=row, column=5)

        color_button = tk.Button(molecule_frame, text=" ",
                                 command=lambda widget=eval(f"{mol_name.lower()}_rowl_field"): choose_color(widget))
        color_button.grid(row=row, column=6)

        exec(f"{mol_name.lower()}_line, = ax1.plot([], [], alpha=0.8, linewidth=1)", globals())
        exec(f"{mol_name.lower()}_line.set_label('{mol_name}')", globals())

        # Intensity calculation
        exec(f"{mol_name.lower()}_intensity = Intensity(mol_{mol_name.lower()})", globals())
        exec(
            f"{mol_name.lower()}_intensity.calc_intensity(t_{mol_name.lower()}, n_mol_{mol_name.lower()}, dv=intrinsic_line_width)",
            globals())
        # print(f"{mol_name.lower()}_intensity")
        # Add the variables to the globals dictionary
        globals()[f"{mol_name.lower()}_intensity"] = eval(f"{mol_name.lower()}_intensity")

        # Spectrum creation
        exec(
            f"{mol_name.lower()}_spectrum = Spectrum(lam_min=min_lamb, lam_max=max_lamb, dlambda=model_pixel_res, R=model_line_width, distance=dist)",
            globals())

        # Adding intensity to the spectrum
        exec(
            f"{mol_name.lower()}_spectrum.add_intensity({mol_name.lower()}_intensity, {mol_name.lower()}_radius ** 2 * np.pi)",
            globals())

        # Fluxes and lambdas
        exec(
            f"fluxes_{mol_name.lower()} = {mol_name.lower()}_spectrum.flux_jy; lambdas_{mol_name.lower()} = {mol_name.lower()}_spectrum.lamgrid",
            globals())

        # delete_button = tk.Button(molecule_frame, text="Delete", command=lambda r=row, mn=mol_name: delete_row(r, mn))
        # delete_button.grid(row=row, column=5)

        nextrow = row + 1

    write_user_csv(molecules_data)
    spanoptionsvar = [m[0] for m in molecules_data]
    spandropd['values'] = spanoptionsvar
    if spanoptionsvar:
        spandropd.set(spanoptionsvar[0])

    filename = os.path.join(save_folder, f"default.csv")
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)  # Read the header row
                for row in reader:
                    mol_name, mol_filepath, mol_label, temp, rad, n_mol, vis = row
                    # Update global variables or GUI fields with the loaded values
                    exec(f"global t_{mol_name.lower()}; t_{mol_name.lower()} = {temp}")
                    exec(f"global {mol_name.lower()}_radius; {mol_name.lower()}_radius = {rad}")
                    exec(f"global n_mol_{mol_name.lower()}; n_mol_{mol_name.lower()} = {n_mol}")
                    exec(f"global {mol_name.lower()}_vis; {mol_name.lower()}_vis = {vis}")

                    # Update GUI fields
                    eval(f"{mol_name.lower()}_temp_field").delete(0, "end")
                    eval(f"{mol_name.lower()}_temp_field").insert(0, temp)

                    eval(f"{mol_name.lower()}_rad_field").delete(0, "end")
                    eval(f"{mol_name.lower()}_rad_field").insert(0, rad)

                    eval(f"{mol_name.lower()}_dens_field").delete(0, "end")
                    eval(f"{mol_name.lower()}_dens_field").insert(0, f"{float(n_mol):.{1}e}")

                    update_initvals()

            # update()
            data_field.delete('1.0', "end")
            data_field.insert('1.0', 'Defaults loaded!')
        except Exception as e:
            print("Error loading defaults:", e)

    for row, (mol_name, _, _) in enumerate(molecules_data, start=1):

        # Get the molecule name in lower case
        mol_name_lower = mol_name.lower()

        # Get the line object
        line_var = globals().get(f"{mol_name_lower}_line")

        # Check if the line object exists and has a color attribute
        if line_var and hasattr(line_var, 'get_color'):
            # Get the color of the line
            line_color = line_var.get_color()
            globals()[f"{mol_name.lower()}_color"] = line_color

            # Get the color button from the grid_slaves list
            color_button = molecule_frame.grid_slaves(row=row, column=6)[0]

            # Set the background color of the color button
            color_button.configure(bg=line_color)

        if eval(f"{mol_name.lower()}_vis"):
            exec(f"{mol_name.lower()}_vis_checkbutton.select()")
    
# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
            
def add_molecule_data():
    global mol_file_path
    global mol_file_name
    global wave_data
    global flux_data
    global filename_box_data
    global nextrow
    global vis_button
    global vis_status
    # global text_box
    # global text_box_data
    global text_boxes
    global molecule_elements
    global deleted_molecules
    global molecules_data
    global files_frame
    global spanoptionsvar
    global spandropd

    molecule_elements = {}

    # Define the filetypes to accept, in this case, only .par files
    molfiletypes = [('PAR Files', '*.par')]
    hitran_directory = os.path.abspath("../HITRANdata")

    # Ask the user to select a data file
    inmolfiles = filedialog.askopenfilename(multiple=True, title='Choose HITRAN Molecule Data File',
                                            filetypes=molfiletypes, initialdir=hitran_directory)

    if inmolfiles:
        for mol_file_path in inmolfiles:
            # Process each selected file
            mol_file_name = os.path.basename(file_path)

            # Ask the user to enter the molecule name
            molecule_name = simpledialog.askstring("Assign label",
                                                   "Enter a label for this model (LaTeX and case sensitive):",
                                                   parent=window)
            molecule_label = molecule_name

            # remove unaccepted characters
            # molecule_name = molecule_name.replace("-","_")
            molecule_name = molecule_name.translate({ord(i): None for i in '_$^{}'})
            molecule_name = molecule_name.translate({ord(i): "_" for i in ' -'})

            # Check if the molecule_name starts with a number
            if molecule_name[0].isdigit():
                # Add a "m_" to the beginning of the molecule name because python cannot take strings starting with a number
                molecule_name = 'm_' + molecule_name

            molecule_name = molecule_name.upper()

            if molecule_name:

                data_field.delete('1.0', "end")
                data_field.insert('1.0', 'Importing Molecule...')
                plt.draw(), canvas.draw()
                fig.canvas.flush_events()

                # Specify the common directory to start the relative path from
                common_directory = "HITRANdata"

                script_directory = os.path.dirname(
                    os.path.realpath(sys.argv[0] if hasattr(sys, 'frozen') else sys.executable))

                # Add the molecule name and file path to the molecules_data list
                relative_path = os.path.relpath(mol_file_path, start=script_directory)
                if common_directory in relative_path:
                    relative_path = os.path.join(common_directory,
                                                 relative_path.split(common_directory, 1)[1].lstrip(
                                                     os.path.sep)).replace('\\', '/')
                molecules_data.append((molecule_name, relative_path, molecule_label))

                # make sure molecule is no longer in deleted array
                if molecule_name.lower() in deleted_molecules:
                    deleted_molecules.remove(molecule_name.lower())

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
                exec(f"mol_{molecule_name.lower()} = MolData('{molecule_name}', '{mol_file_path}')", globals())
                exec(f"scale_exponent_{molecule_name.lower()} = {scale_exponent}", globals())
                exec(f"scale_number_{molecule_name.lower()} = {scale_number}", globals())
                exec(f"n_mol_{molecule_name.lower()}_init = {n_mol_init}", globals())
                exec(f"t_kin_{molecule_name.lower()} = {t_kin}", globals())
                exec(f"{molecule_name.lower()}_radius_init = {radius_init}", globals())

                # Print the results (you can modify this part as needed)
                print(f"Molecule Added: {molecule_name}")
                # print(f"scale_exponent_{molecule_name.lower()} = {scale_exponent}")
                # print(f"scale_number_{molecule_name.lower()} = {scale_number}")
                # print(f"n_mol_{molecule_name.lower()}_init = {n_mol_init}")
                # print(f"t_kin_{molecule_name.lower()} = {t_kin}")
                # print(f"{molecule_name.lower()}_radius_init = {radius_init}")
                print()  # Empty line for spacing

                # Store the initial values in the dictionary
                initial_values[molecule_name.lower()] = {
                    "scale_exponent": scale_exponent,
                    "scale_number": scale_number,
                    "t_kin": t_kin,
                    "radius_init": radius_init,
                    "n_mol_init": n_mol_init
                }

                # Create a new row of text boxes for the current molecule
                row = nextrow
                y_row = start_y + row_height * (num_rows - row - 1)

                # Row label
                exec(f"{molecule_name.lower()}_rowl_field = tk.Entry(molecule_frame, width=6)", globals())
                eval(f"{molecule_name.lower()}_rowl_field").grid(row=row, column=0)
                eval(f"{molecule_name.lower()}_rowl_field").insert(0, f"{molecule_name}")
                molecule_elements[molecule_name.lower()] = {'rowl': molecule_name.lower() + '_rowl_field'}

                # Temperature input field
                globals()[f"{molecule_name.lower()}_temp_field"] = tk.Entry(molecule_frame, width=4)

                eval(f"{molecule_name.lower()}_temp_field").grid(row=row, column=1)
                eval(f"{molecule_name.lower()}_temp_field").insert(0, f"{t_kin}")
                # globals() [f"{molecule_name.lower()}_submit_temp_button"] = tk.Button(window, text="Submit", command=lambda mn=molecule_name.lower(), te = globals()[f"{molecule_name.lower()}_temp_field"]: submit_temp(te.get(), mn))
                # eval(f"{molecule_name.lower()}_submit_temp_button").grid(row=row + 1, column=2)
                molecule_elements[molecule_name.lower()] = {'temp': molecule_name.lower() + '_temp_field'}
                eval(f"{molecule_name.lower()}_temp_field").bind("<Return>", lambda event, mn=molecule_name.lower(),
                                                                                    ce=globals()[
                                                                                        f"{molecule_name.lower()}_temp_field"]: submit_temp(
                    ce.get(), mn))

                # Radius input field
                globals()[f"{molecule_name.lower()}_rad_field"] = tk.Entry(molecule_frame, width=4)
                eval(f"{molecule_name.lower()}_rad_field").grid(row=row, column=2)
                eval(f"{molecule_name.lower()}_rad_field").insert(0, f"{radius_init}")
                # globals() [f"{molecule_name.lower()}_submit_rad_button"] = tk.Button(window, text="Submit", command=lambda mn=mol_name.lower(), re = globals()[f"{molecule_name.lower()}_rad_field"]: submit_rad(re.get(), mn))
                # eval(f"{molecule_name.lower()}_submit_rad_button").grid(row=row + 1, column=4)
                molecule_elements[molecule_name.lower()]['rad'] = molecule_name.lower() + '_rad_field'
                eval(f"{molecule_name.lower()}_rad_field").bind("<Return>", lambda event, mn=molecule_name.lower(),
                                                                                   ce=globals()[
                                                                                       f"{molecule_name.lower()}_rad_field"]: submit_rad(
                    ce.get(), mn))

                # Column Density input field
                globals()[f"{molecule_name.lower()}_dens_field"] = tk.Entry(molecule_frame, width=6)
                eval(f"{molecule_name.lower()}_dens_field").grid(row=row, column=3)
                eval(f"{molecule_name.lower()}_dens_field").insert(0, f"{n_mol_init:.{1}e}")
                # globals() [f"{molecule_name.lower()}_submit_col_button"] = tk.Button(window, text="Submit", command=lambda mn=mol_name.lower(), ce = globals()[f"{molecule_name.lower()}_dens_field"]: submit_col(ce.get(), mn))
                # eval(f"{molecule_name.lower()}_submit_col_button").grid(row=row + 1, column=6)
                molecule_elements[molecule_name.lower()]['dens'] = molecule_name.lower() + '_dens_field'
                eval(f"{molecule_name.lower()}_dens_field").bind("<Return>", lambda event, mn=molecule_name.lower(),
                                                                                    ce=globals()[
                                                                                        f"{molecule_name.lower()}_dens_field"]: submit_col(
                    ce.get(), mn))

                # Visibility Button
                globals()[f"{molecule_name.lower()}_vis_status"] = tk.BooleanVar()
                globals()[f"{molecule_name.lower()}_vis_checkbutton"] = tk.Checkbutton(molecule_frame, text='',
                                                                                       variable=eval(
                                                                                           f"{molecule_name.lower()}_vis_status"),
                                                                                       command=lambda
                                                                                           mn=molecule_name.lower(): model_visible(
                                                                                           mn))
                globals()[f"{molecule_name.lower()}_vis_status"].set(False)  # Set the initial state
                eval(f"{molecule_name.lower()}_vis_checkbutton").grid(row=row, column=4)
                globals()[f"{molecule_name.lower()}_vis"] = False
                # Add the variable to the globals dictionary
                # Add the text boxes to the molecule_text_boxes dictionary
                # molecule_text_boxes[molecule_name.lower()] = text_boxes

                # print(f"{mol_name.lower()}_rowl_field")

                del_button = tk.Button(molecule_frame, text="X", command=lambda
                    widget=eval(f"{molecule_name.lower()}_rowl_field"): delete_row(widget))
                del_button.grid(row=row, column=5)

                color_button = tk.Button(molecule_frame, text=" ", command=lambda
                    widget=eval(f"{molecule_name.lower()}_rowl_field"): choose_color(widget))
                color_button.grid(row=row, column=6)

                # Increment nextrow
                nextrow += 1

                exec(f"{molecule_name.lower()}_line, = ax1.plot([], [], alpha=0.8, linewidth=1)", globals())
                exec(f"{molecule_name.lower()}_line.set_label('{molecule_label}')", globals())

                line_var = globals().get(f"{molecule_name.lower()}_line")
                linecolor = line_var.get_color()
                # Get the color button from the grid_slaves list
                colorbutton = molecule_frame.grid_slaves(row=row, column=6)[0]

                # Set the background color of the color button
                colorbutton.configure(bg=linecolor)

                # Column density
                exec(
                    f"global n_mol_{molecule_name.lower()}; n_mol_{molecule_name.lower()} = n_mol_{molecule_name.lower()}_init")

                # Temperature
                exec(f"global t_{molecule_name.lower()}; t_{molecule_name.lower()} = t_kin_{molecule_name.lower()}")

                # Radius
                exec(
                    f"global {molecule_name.lower()}_radius; {molecule_name.lower()}_radius = {molecule_name.lower()}_radius_init")

                # Intensity calculation
                exec(f"{molecule_name.lower()}_intensity = Intensity(mol_{molecule_name.lower()})", globals())
                exec(
                    f"{molecule_name.lower()}_intensity.calc_intensity(t_{molecule_name.lower()}, n_mol_{molecule_name.lower()}, dv=intrinsic_line_width)",
                    globals())
                # print(f"{molecule_name.lower()}_intensity")
                # Add the variables to the globals dictionary
                globals()[f"{molecule_name.lower()}_intensity"] = eval(f"{molecule_name.lower()}_intensity")

                # Spectrum creation
                exec(
                    f"{molecule_name.lower()}_spectrum = Spectrum(lam_min=min_lamb, lam_max=max_lamb, dlambda=model_pixel_res, R=model_line_width, distance=dist)",
                    globals())

                # Adding intensity to the spectrum
                exec(
                    f"{molecule_name.lower()}_spectrum.add_intensity({molecule_name.lower()}_intensity, {molecule_name.lower()}_radius ** 2 * np.pi)",
                    globals())

                # Fluxes and lambdas
                exec(
                    f"fluxes_{molecule_name.lower()} = {molecule_name.lower()}_spectrum.flux_jy; lambdas_{molecule_name.lower()} = {molecule_name.lower()}_spectrum.lamgrid",
                    globals())

                # Dynamically set the data for each molecule's line using exec and globals()
                # exec(f"{molecule_name.lower()}_line.set_data(lambdas_{molecule_name.lower()}, fluxes_{molecule_name.lower()})", globals())

                # Save the molecules_data to the CSV file
                write_user_csv(molecules_data)

                update()

                # Clearing the text feed box.
                data_field.delete('1.0', "end")
                data_field.insert('1.0', 'Molecule Imported')
                canvas.draw(), plt.draw()
                # fig.canvas.flush_events()

                # plt.pause(2)
                # Sleep for 3 seconds
                # time.sleep(3)
                canvas.draw()

                # Clearing the text feed box.
                data_field.delete('1.0', "end")

                canvas.draw()

                spanoptionsvar = [m[0] for m in molecules_data]
                spandropd['values'] = spanoptionsvar
                if spanoptionsvar:
                    spandropd.set(spanoptionsvar[0])


            else:
                print("Molecule label not provided.")
    else:
        print("No files selected.")

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
            
def del_molecule_data():
    global molecules_data, nextrow

    default_list = []
    try:
        with open(os.path.join(save_folder, "default.csv"), 'r') as list_file:
            reader = csv.reader(list_file)
            next(reader)  # Skip header
            for row in reader:
                default_list.append(tuple(row[:3]))  # Taking the first three columns of each row
    except Exception as e:
        print("Error reading molecules_list.csv:", e)

    # Create a set of molecule names from molecules_data
    default_data_names = set(item[0] for item in default_data)
    indexsub = 0
    for row, (mol_name, _, _) in enumerate(molecules_data, start=1):
        if mol_name not in default_data_names:
            adjrow = row - indexsub
            # Destroy all widgets in the row
            for w in molecule_frame.grid_slaves(row=adjrow):
                w.destroy()

            exec(f"{mol_name.lower()}_line.remove()", globals())

            # Remove the molecule from molecules_data
            molecules_data = [molecule for molecule in molecules_data if molecule[0].lower() != mol_name]

            # Move all rows below this row up by one
            for r in range(adjrow + 1, nextrow):
                for col in range(7):  # Adjust the range if you have more columns
                    widget_list = molecule_frame.grid_slaves(row=r, column=col)
                    for widget in widget_list:
                        widget.grid(row=r - 1, column=col)

            indexsub += 1

    write_user_csv(molecules_data)
    nextrow = 7
    update()

    data_field.delete('1.0', "end")
    data_field.insert('1.0', f'{mol_name.upper()} deleted!')





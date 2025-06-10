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
# -----------------------------------------------------------------------------

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
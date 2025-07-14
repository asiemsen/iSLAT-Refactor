
def submitField(event, text):
    # global text_box
    # global text_box_data

    data_field.delete ('1.0', "end")
    data_field.insert ('1.0', 'Submitting Radius...')
    plt.draw (), canvas.draw ()
    fig.canvas.flush_events ()

    val = float (event)
    exec (f"{text}_radius = {val}", globals ())

    # Intensity calculation
    exec (f"{text}_intensity.calc_intensity(t_{text}, n_mol_{text}, dv=intrinsic_line_width)", globals ())

    # Spectrum creation
    exec (
        f"{text}_spectrum = Spectrum(lam_min=min_lamb, lam_max=max_lamb, dlambda=model_pixel_res, R=model_line_width, distance=dist)",
        globals ())

    # Adding intensity to the spectrum
    exec (f"{text}_spectrum.add_intensity({text}_intensity, {text}_radius ** 2 * np.pi)", globals ())

    # Fluxes and lambdas
    exec (f"fluxes_{text} = {text}_spectrum.flux_jy; lambdas_{text} = {text}_spectrum.lamgrid", globals ())

    # Dynamically set the data for each molecule's line using exec and globals()
    exec (f"{text}_line.set_data(lambdas_{text}, fluxes_{text})", globals ())

    # Clearing the text feed box.
    data_field.delete ('1.0', "end")
    data_field.insert ('1.0', 'Radius updated!')
    plt.draw (), canvas.draw ()
    fig.canvas.flush_events ()

    # Clearing the text feed box.
    data_field.delete ('1.0', "end")
    plt.draw (), canvas.draw ()

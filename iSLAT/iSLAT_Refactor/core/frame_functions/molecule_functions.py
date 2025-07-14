
import numpy as np

from iSLAT_Refactor import app_globals
from ir_model.intensity import Intensity

def submitField(field, event, text, appController):

    molDict = appController.moleculeManager.moleculeDictionary
    mol = molDict[text.lower()]

    data_field.delete ('1.0', "end")
    data_field.insert ('1.0', 'Submitting Radius...')
    plt.draw (), canvas.draw ()
    fig.canvas.flush_events ()

    val = float(event)

    if field == "temp":
        mol["t_kin"] = val
    elif field == "col":
        mol["n_mol"] = val
    elif field == "rad":
        mol["rad"] = val
    
    mol["radius"] = val

    # Intensity calculation
    if field != "rad":
        mol["intensity"].intensity.calc_intensity(mol["t_kin"], mol["n_mol"], dv = app_globals.intrinsic_line_width)

    # Spectrum creation
    mol["spectrum"] = Spectrum(lam_min=app_globals.min_lamb, 
                                       lam_max=app_globals.max_lamb, 
                                       dlambda=app_globals.model_pixel_res,
                                       R=app_globals.model_line_width,
                                       distance=app_globals.dist)

    # Adding intensity to the spectrum
    mol["spectrum"].add_intensity(mol["intensity"], mol["radius"] ** 2 * np.pi)

    # Fluxes and lambdas
    mol["fluxes"] = mol["spectrum"].flux_jy
    mol["lambdas"] = mol["spectrum"].lamgrid

    # Dynamically set the data for each molecule's line using exec and globals()
    mol["line_plot"].set_data(mol["lambdas"], mol["fluxes"])


    # Clearing the text feed box.
    data_field.delete ('1.0', "end")
    data_field.insert ('1.0', 'Radius updated!')
    plt.draw (), canvas.draw ()
    fig.canvas.flush_events ()

    # Clearing the text feed box.
    data_field.delete ('1.0', "end")
    plt.draw (), canvas.draw ()

    

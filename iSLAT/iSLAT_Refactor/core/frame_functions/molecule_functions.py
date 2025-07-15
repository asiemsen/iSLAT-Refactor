
import numpy as np
import matplotlib.pyplot as plt


from iSLAT_Refactor import app_globals


def submitField(field, text, appController):

    molDict = appController.moleculeManager.moleculeDictionary
    molName = text.lower()
    mol = molDict[molName]

    # create method for this 
    appController.guiManager.text_frame.data_field.delete('1.0', "end")
    appController.guiManager.text_frame.data_field.insert('1.0', 'Submitting Radius...')
    plt.draw ()
    appController.guiManager.canvas.draw()
    appController.guiManager.fig.canvas.flush_events()

    if field == "temp":
        val = appController.guiManager.molecules_frame.inputFields[molName]["temp"].get()
        floatConvert(val, appController)
        mol["t_kin"] = float(val)
    elif field == "col":
        val = appController.guiManager.molecules_frame.inputFields[molName]["n_mol"].get()
        floatConvert(val, appController)
        mol["n_mol"] = float(val)
    elif field == "rad":
        val = appController.guiManager.molecules_frame.inputFields[molName]["radius"].get()
        floatConvert(val, appController)
        mol["radius"] = float(val)

    # Intensity calculation
    # if field != "rad":
    print("DEBUG: t_kin =", mol["t_kin"], type(mol["t_kin"]))

    mol["intensity"].calc_intensity(mol["t_kin"], mol["n_mol"], dv = app_globals.intrinsic_line_width)

    # Spectrum creation
    appController.moleculeManager.createSpectrum(molName)

    # Adding intensity to the spectrum
    mol["spectrum"].add_intensity(mol["intensity"], mol["radius"] ** 2 * np.pi)

    # Fluxes and lambdas
    mol["fluxes"] = mol["spectrum"].flux_jy
    mol["lambdas"] = mol["spectrum"].lamgrid

    # Dynamically set the data for each molecule's line using exec and globals()
    mol["line_plot"].set_data(mol["lambdas"], mol["fluxes"])


    # Clearing the text feed box.
    appController.guiManager.text_frame.data_field.delete ('1.0', "end")
    appController.guiManager.text_frame.data_field.insert ('1.0', 'Radius updated!')
    # plt.draw (), canvas.draw ()
    appController.guiManager.fig.canvas.flush_events()

    # Clearing the text feed box.
    appController.guiManager.text_frame.data_field.delete ('1.0', "end")
    plt.draw ()
    appController.guiManager.canvas.draw()

    

def floatConvert(val, appController):
    try:
        floatVal = float(val)
        print("value correctly converted: ", floatVal)
    except ValueError:
        print("value not correctly converted: ", floatVal)
        appController.guiManager.text_frame.data_field.delete('1.0', "end")
        appController.guiManager.text_frame.data_field.insert('1.0', "Invalid input: must be a number.")
        return




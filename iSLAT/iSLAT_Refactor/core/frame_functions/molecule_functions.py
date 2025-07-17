
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt

from iSLAT_Refactor import app_globals

def submitField(field, text, appController):

    molDict = appController.moleculeManager.moleculeDictionary
    molName = text.lower()
    mol = molDict[molName]

    displayMessage(appController, "Submitting Radius...")

    plt.draw ()
    appController.guiManager.canvas.draw()
    appController.guiManager.fig.canvas.flush_events()

    if field == "temp":
        val = appController.guiManager.molecules_frame.inputFields[molName]["temp"].get()
        floatConvert(val, appController)
        mol["t_kin"] = float(val)
    elif field == "density":
        val = appController.guiManager.molecules_frame.inputFields[molName]["density"].get()
        floatConvert(val, appController)
        mol["n_mol"] = float(val)
    elif field == "radius":
        val = appController.guiManager.molecules_frame.inputFields[molName]["radius"].get()
        floatConvert(val, appController)
        mol["radius"] = float(val)

    # Intensity calculation
    # if field != "rad":
    print(f"temp = {mol["t_kin"]}, column = {mol["n_mol"]}, rad = {mol["radius"]}")

    mol["intensity"].calc_intensity(mol["t_kin"], mol["n_mol"], dv = app_globals.intrinsic_line_width)

    # Spectrum creation
    appController.moleculeManager.createSpectrum(molName)

    # Adding intensity to the spectrum
    # mol["spectrum"].add_intensity(mol["intensity"], mol["radius"] ** 2 * np.pi)

    # Fluxes and lambdas
    mol["fluxes"] = mol["spectrum"].flux_jy
    mol["lambdas"] = mol["spectrum"].lamgrid

    # Dynamically set the data for each molecule's line using exec and globals()
    mol["line_plot"].set_data(mol["lambdas"], mol["fluxes"])


    # Clearing the text feed box.
    displayMessage(appController, "Radius updated!")
    # plt.draw (), canvas.draw ()
    appController.guiManager.fig.canvas.flush_events()

    # Clearing the text feed box.
    appController.guiManager.text_frame.data_field.delete ('1.0', "end")
    plt.draw ()
    appController.moleculeManager.calcSum(appController.guiManager.ax1, appController.guiManager.canvas)


def delete_row(appController, widget, data_frame, molName):
    moleculesData = appController.moleculeManager.molecules_data

    # data_field.delete ('1.0', "end")
    print(f"deleting {molName}")

    if molName == "h2o":
        displayMessage(appController, f'You can not delete {molName.upper()}!')
        return
    
    row = widget.grid_info()["row"]

    

    # Destroy all widgets in the row
    for w in data_frame.grid_slaves(row=row):
        if isinstance(w, tk.Entry) or isinstance(w, tk.Button) or isinstance(w, tk.Checkbutton):
            w.unbind('<Enter>')
            w.unbind('<Leave>')
        w.destroy()

    # exec (f"{mol_name.lower ()}_line.remove()", globals ())
    appController.moleculeManager.moleculeDictionary[molName]["line_plot"].remove()

    # Remove the molecule from molecules_data
    moleculesData = [molecule for molecule in moleculesData if molecule[0].lower () != molName]
    appController.moleculeManager.molecules_data = moleculesData

    # write_user_csv(molecules_data)
    del appController.moleculeManager.moleculeDictionary[molName]
    nextrow = len(appController.moleculeManager.moleculeDictionary)

    # Move all rows below this row up by one
    for r in range (row + 1, nextrow):
        for col in range (7):  # Adjust the range if you have more columns
            widget_list = data_frame.grid_slaves (row=r, column=col)
            for widget in widget_list:
                widget.grid (row=r - 1, column=col)


    # spanoptionsvar = [m[0] for m in molecules_data]
    # spandropd['values'] = spanoptionsvar
    # if spanoptionsvar:
    #     spandropd.set (spanoptionsvar[0])
    # update()
    appController.guiManager.canvas.draw()
    displayMessage(appController, f'{molName.upper ()} deleted!')

def floatConvert(val, appController):
    try:
        floatVal = float(val)
        print("value correctly converted: ", floatVal)
    except ValueError:
        print("value not correctly converted: ", floatVal)
        appController.guiManager.text_frame.data_field.delete('1.0', "end")
        appController.guiManager.text_frame.data_field.insert('1.0', "Invalid input: must be a number.")
        return
    
def displayMessage(appController, message):
    appController.guiManager.text_frame.data_field.delete('1.0', "end")
    appController.guiManager.text_frame.data_field.insert('1.0', message)

    





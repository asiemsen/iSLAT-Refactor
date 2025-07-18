from iSLAT_Refactor import app_globals
import numpy as np

def update_xp1_rng(plotparams, attr, appController):
    
    if attr == "xp1":
        rng = app_globals.rng
        xp1 = float(plotparams.xp1_entry.get())
        app_globals.xp1 = xp1
        xp2 = xp1 + rng
        check_bounds(plotparams, xp1, xp2)
    elif attr == "rng":
        xp1 = app_globals.xp1
        rng = float(plotparams.rng_entry.get())
        app_globals.rng = rng
        xp2 = xp1 + rng
        check_bounds(plotparams, app_globals.xp1, xp2)

    appController.guiManager.ax1.set_xlim(xmin=xp1, xmax=xp2)
    print (f"Updated values: xp1 = {xp1}, rng = {rng}")
    appController.guiManager.canvas.draw()

    

def check_bounds(plotparams, xp1, xp2):
    
    if xp1 < app_globals.min_lamb or xp1 > app_globals.max_lamb:
        if xp1 < app_globals.min_lamb:
            app_globals.min_lamb = xp1
            plotparams.min_lamb_entry.delete(0, "end")
            plotparams.min_lamb_entry.insert(0, str(app_globals.min_lamb))
            
        if xp1 > app_globals.max_lamb:
            app_globals.max_lamb = xp2
            plotparams.max_lamb_entry.delete(0, "end")
            plotparams.max_lamb_entry.insert(0, str(app_globals.max_lamb))
        update_initvals(plotparams)
        
            

def update_initvals(plotparams):
    print("in initvals")
    # Get the values from the Tkinter Entry widgets and convert them to floats
    app_globals.min_lamb = float(plotparams.min_lamb_entry.get())
    app_globals.max_lamb = float(plotparams.max_lamb_entry.get())
    app_globals.dist = float(plotparams.dist_entry.get())
    app_globals.fwhm = float(plotparams.fwhm_entry.get())
    if app_globals.fwhm >= 70:
        app_globals.pix_per_fwhm = 10
    if app_globals.fwhm < 70:
        app_globals.pix_per_fwhm = 20  # increase model pixel sampling in case of higher resolution spectra, usually in the M band
    app_globals.intrinsic_line_width = float (plotparams.intrinsic_line_width_entry.get())
    app_globals.model_line_width = app_globals.cc / app_globals.fwhm
    app_globals.model_pixel_res = (np.mean ([app_globals.min_lamb, app_globals.max_lamb]) / app_globals.cc * app_globals.fwhm) / app_globals.pix_per_fwhm
    # this below needs to be updated to act on the wave array in the data
    app_globals.wave_data = app_globals.wave_original - (app_globals.wave_original / app_globals.cc * float (plotparams.star_rv_entry.get()))

    # data_field.delete ('1.0', "end")
    # data_field.insert ('1.0', 'Parameter updated!')


def updateSpectrum(plotparams, attr, appController):
    print(f"updating spectrum with change to {attr}")
    molDict = appController.moleculeManager.moleculeDictionary
    if attr == "min_lamb":
        try:
            app_globals.min_lamb = float(plotparams.min_lamb_entry.get())
        except ValueError:
            print("Invalid min_lamb input")
    elif attr == "max_lamb":
        try:
            app_globals.max_lamb = float(plotparams.max_lamb_entry.get())
        except ValueError:
            print("Invalid min_lamb input")

    print(f"updating spectrum with change to {attr}")
    print(f"min_lamb = {app_globals.min_lamb}, max_lamb = {app_globals.max_lamb}")

    for molName in molDict:
        mol = molDict[molName]
        mask = (mol["lambdas"] >= app_globals.min_lamb) & (mol["lambdas"] <= app_globals.max_lamb)
        mol["line_plot"].set_data(mol["lambdas"][mask], mol["fluxes"][mask])

    appController.moleculeManager.calcSum(appController.guiManager.ax1, appController.guiManager.canvas)

def generic_submit(plotparams, appController):
    update_initvals(plotparams)
    appController.guiManager.canvas.draw()

def dist_submit(plotparams, appController):
    app_globals.dist = float(plotparams.dist_entry.get())

    molDict = appController.moleculeManager.moleculeDictionary

    for molName in molDict:
        mol = molDict[molName]

        mol["spectrum"]._distance = app_globals.dist
        mol["spectrum"]._flux_jy = None
        mol["spectrum"]._flux = None 
        

    
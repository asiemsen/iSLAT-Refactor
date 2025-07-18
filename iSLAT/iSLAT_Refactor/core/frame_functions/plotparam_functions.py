from iSLAT_Refactor import app_globals as ag
import numpy as np

def update_xp1_rng(plotparams, attr, appController):
    
    if attr == "xp1":
        rng = ag.rng
        xp1 = float(plotparams.xp1_entry.get())
        ag.xp1 = xp1
        xp2 = xp1 + rng
        check_bounds(plotparams, xp1, xp2)
    elif attr == "rng":
        xp1 = ag.xp1
        rng = float(plotparams.rng_entry.get())
        ag.rng = rng
        xp2 = xp1 + rng
        check_bounds(plotparams, ag.xp1, xp2)

    appController.guiManager.ax1.set_xlim(xmin=xp1, xmax=xp2)
    print (f"Updated values: xp1 = {xp1}, rng = {rng}")
    appController.guiManager.canvas.draw()

    

def check_bounds(plotparams, xp1, xp2):
    
    if xp1 < ag.min_lamb or xp1 > ag.max_lamb:
        if xp1 < ag.min_lamb:
            ag.min_lamb = xp1
            plotparams.min_lamb_entry.delete(0, "end")
            plotparams.min_lamb_entry.insert(0, str(ag.min_lamb))
            
        if xp1 > ag.max_lamb:
            ag.max_lamb = xp2
            plotparams.max_lamb_entry.delete(0, "end")
            plotparams.max_lamb_entry.insert(0, str(ag.max_lamb))
        update_initvals(plotparams)
        
            

def update_initvals(plotparams):
    print("in initvals")
    # Get the values from the Tkinter Entry widgets and convert them to floats
    ag.min_lamb = float(plotparams.min_lamb_entry.get())
    ag.max_lamb = float(plotparams.max_lamb_entry.get())
    ag.dist = float(plotparams.dist_entry.get())
    ag.fwhm = float(plotparams.fwhm_entry.get())
    if ag.fwhm >= 70:
        ag.pix_per_fwhm = 10
    if ag.fwhm < 70:
        ag.pix_per_fwhm = 20  # increase model pixel sampling in case of higher resolution spectra, usually in the M band
    ag.intrinsic_line_width = float (plotparams.intrinsic_line_width_entry.get())
    ag.model_line_width = ag.cc / ag.fwhm
    ag.model_pixel_res = (np.mean ([ag.min_lamb, ag.max_lamb]) / ag.cc * ag.fwhm) / ag.pix_per_fwhm
    # this below needs to be updated to act on the wave array in the data
    ag.wave_data = ag.wave_original - (ag.wave_original / ag.cc * float (plotparams.star_rv_entry.get()))

    # data_field.delete ('1.0', "end")
    # data_field.insert ('1.0', 'Parameter updated!')


def updateSpectrum(plotparams, attr, appController):
    print(f"updating spectrum with change to {attr}")
    molDict = appController.moleculeManager.moleculeDictionary
    if attr == "min_lamb":
        try:
            ag.min_lamb = float(plotparams.min_lamb_entry.get())
        except ValueError:
            print("Invalid min_lamb input")
    elif attr == "max_lamb":
        try:
            ag.max_lamb = float(plotparams.max_lamb_entry.get())
        except ValueError:
            print("Invalid min_lamb input")

    print(f"updating spectrum with change to {attr}")
    print(f"min_lamb = {ag.min_lamb}, max_lamb = {ag.max_lamb}")

    for molName in molDict:
        mol = molDict[molName]
        mask = (mol["lambdas"] >= ag.min_lamb) & (mol["lambdas"] <= ag.max_lamb)
        mol["line_plot"].set_data(mol["lambdas"][mask], mol["fluxes"][mask])

    appController.moleculeManager.calcSum(appController.guiManager.ax1, appController.guiManager.canvas)

def generic_submit(plotparams, appController):
    update_initvals(plotparams)
    appController.guiManager.canvas.draw()

def dist_submit(plotparams, appController):
    
    ag.dist = float(plotparams.dist_entry.get())

    print(f"changing distance to {ag.dist}")

    molDict = appController.moleculeManager.moleculeDictionary
    
    for molName in molDict:
        mol = molDict[molName]
        mask = (mol["lambdas"] >= ag.min_lamb) & (mol["lambdas"] <= ag.max_lamb)

        mol["spectrum"]._distance = ag.dist
        mol["spectrum"]._flux_jy = None
        mol["spectrum"]._flux = None 

        mol["fluxes"] = mol["spectrum"].flux_jy
        mol["lambdas"] = mol["spectrum"].lamgrid

        mol["line_plot"].set_data(mol["lambdas"][mask], mol["fluxes"][mask])

    appController.calculateSum()
        
def stellar_submit(plotparams, appController):
    ag.wave_data = wave_data = ag.wave_original - (ag.wave_original / ag.cc * float (plotparams.star_rv_entry.get()))
    appController.guiManager.data_line.set_data(ag.wave_data, ag.flux_data)
    appController.drawCanvas()

    
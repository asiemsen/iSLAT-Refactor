

import numpy as np
import matplotlib.pyplot as plt

from iSLAT_Refactor import app_globals
from ir_model.moldata import MolData
from ir_model.intensity import Intensity
from ir_model.spectrum import Spectrum

class MoleculeManager: 

    def __init__(self, molecules_data) -> None:


        self.fill = None
        self.propNum = 0
        self.moleculeDictionary = {}

        for mol_name, mol_filepath, mol_label in molecules_data:

            molName = mol_name.lower()

            params = app_globals.INITIAL_PARAMETERS.get(mol_name, app_globals.DEFAULT_INITIAL_PARAMS)
            scale_exponent = params["scale_exponent"]
            scale_number = params["scale_number"]
            t_kin = params["t_kin"]
            radius_init = params["radius_init"]

            # Calculate and set n_mol_init for the current molecule
            n_mol_init = float (scale_number * (10 ** scale_exponent))

            if molName not in self.moleculeDictionary:
                self.moleculeDictionary[molName] = {}

            mol = self.moleculeDictionary[molName]

            mol["is_visible"] = False

            if molName == "h2o":
                mol["is_visible"] = True

            print(f"MolData values: mol_name = {mol_name}, mol_filepath = {mol_filepath}")
            mol["data"] = MolData(mol_name, mol_filepath)
            mol["scale_exponent"] = scale_exponent
            mol["scale_number"] = scale_number
            mol["t_kin"] = t_kin   # t_kin vs t?
            mol["radius"] = radius_init
            mol["n_mol"] = n_mol_init # what is n_mol (column density?)
            mol["label"] = mol_label

            if molName == 'h2o':
                print(f"temp = {mol["t_kin"]}, column = {mol["n_mol"]}, rad = {mol["radius"]}")


            # Intensity create/calc
            mol["intensity"] = Intensity(mol["data"])
            mol["intensity"].calc_intensity(mol["t_kin"], mol["n_mol"], dv = app_globals.intrinsic_line_width)

            # Spectrum creation/calc
            self.createSpectrum(molName)
            
            # Fluxes and Lambdas
            mol["fluxes"] = mol["spectrum"].flux_jy
            mol["lambdas"] = mol["spectrum"].lamgrid


            prop_cycle = app_globals.COLOR_CYCLE
            color = prop_cycle[self.propNum]
            mol["color"] = color
        

            print (f"Molecule Initialized: {mol_name}")

            self.propNum += 1


    def createLines(self, molecules_data, ax1):
        for mol_name, mol_filepath, mol_label in molecules_data:
            

            molName = mol_name.lower()
            mol = self.moleculeDictionary[molName]

            
            if mol["is_visible"]:
                mol["line_plot"], = ax1.plot(mol["spectrum"].lamgrid, mol["fluxes"], alpha = 0.8, linewidth = 1.0, ls = '--')
                mol["line_plot"].set_label(mol_label)
            else:
                mol["line_plot"], = ax1.plot(mol["spectrum"].lamgrid, mol["fluxes"], alpha=0.0, linewidth=1.0, ls = '--')
            ax1.legend(loc='upper right')

    def toggle_visible(self, molName, ax1, canvas):

        molName = molName.lower()
        mol = self.moleculeDictionary[molName]
        mol["is_visible"] = not mol["is_visible"]



        if mol["is_visible"]:
            mol["line_plot"].set_alpha(0.8)
            mol["line_plot"].set_label(mol["label"])

            # change alpha to 0.8
        else:
            mol["line_plot"].set_alpha(0.0)
            mol["line_plot"].set_label(None)
            # change alpha to 0.0
        ax1.legend(loc='upper right')

        self.calcSum(ax1, canvas)
        
        plt.draw()
    
    def calcSum(self, ax1, canvas):
        totalFluxes = []

        for i in range(len(self.moleculeDictionary['h2o']['lambdas'])):
            
            fluxSum = 0
            for molName in self.moleculeDictionary:
                mol = self.moleculeDictionary[molName]
                if mol["is_visible"]:
                    fluxSum += mol["fluxes"][i]
        
            totalFluxes.append(fluxSum)
        if self.fill is not None:
            self.fill.remove()

        self.fill = ax1.fill_between(self.moleculeDictionary['h2o']['lambdas'], totalFluxes, color='gray', alpha=1)

        canvas.draw()

    def createSpectrum(self, molName):
        mol = self.moleculeDictionary[molName]

        mol["spectrum"] = Spectrum(lam_min=app_globals.min_lamb, 
                                       lam_max=app_globals.max_lamb, 
                                       dlambda=app_globals.model_pixel_res,
                                       R=app_globals.model_line_width,
                                       distance=app_globals.dist)
            
        mol["spectrum"].add_intensity(mol["intensity"], mol["radius"] ** 2 * np.pi)


# @dataclass
# class Molecule:
#     data: MolData
#     scale_exponent: float
#     scale_number: float
#     t_kin: float
#     radius_init: float
#     n_mol_init: float
# 
# self.moleculeDictionary[molName] = Molecule(...)





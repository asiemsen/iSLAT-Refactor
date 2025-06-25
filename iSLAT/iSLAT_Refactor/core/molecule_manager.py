import numpy as np

from iSLAT_Refactor import app_globals
from ir_model.moldata import MolData
from ir_model.intensity import Intensity
from ir_model.spectrum import Spectrum

class MoleculeManager: 

    def __init__(self, molecules_data) -> None:

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

            mol["data"] = MolData(mol_name, mol_filepath)
            mol["scale_exponent"] = scale_exponent
            mol["scale_number"] = scale_number
            mol["t_kin"] = t_kin   # t_kin vs t?
            mol["radius"] = radius_init
            mol["n_mol"] = n_mol_init # what is n_mol (column density?)

            # Intensity create/calc
            mol["intensity"] = Intensity(mol["data"])
            mol["intensity"].calc_intensity(mol["t_kin"], mol["n_mol"], dv = app_globals.intrinsic_line_width)

            # Spectrum creation/calc
            mol["spectrum"] = Spectrum(lam_min=app_globals.min_lamb, 
                                       lam_max=app_globals.max_lamb, 
                                       dlambda=app_globals.model_pixel_res,
                                       R=app_globals.model_line_width,
                                       distance=app_globals.dist)
            
            mol["spectrum"].add_intensity(mol["intensity"], mol["radius"] ** 2 * np.pi)
            
            # Fluxes and Lambdas
            mol["fluxes"] = mol["spectrum"].flux_jy
            mol["lambdas"] = mol["spectrum"].lamgrid


            print (f"Molecule Initialized: {mol_name}")



    def createLines(self, molecules_data, ax1):
        for mol_name, mol_filepath, mol_label in molecules_data:

            molName = mol_name.lower()
            mol = self.moleculeDictionary[molName]

            
            if molName == 'h2o':
                mol["line_plot"], = ax1.plot(mol["spectrum"].lamgrid, mol["fluxes"], alpha = 0.8, linewidth = 1.0)
        





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





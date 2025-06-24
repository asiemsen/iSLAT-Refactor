from iSLAT_Refactor.app_globals import INITIAL_PARAMETERS, DEFAULT_INITIAL_PARAMS, intrinsic_line_width
from ir_model.moldata import MolData
from ir_model.intensity import Intensity
from ir_model.spectrum import Spectrum

class MoleculeManager: 

    def __init__(self, molecules_data) -> None:

        self.moleculeDictionary = {}

        for mol_name, mol_filepath, mol_label in molecules_data:

            molName = mol_name.lower()

            params = INITIAL_PARAMETERS.get(mol_name, DEFAULT_INITIAL_PARAMS)
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
            mol["intensity"].calcIntensity(mol["t_kin"], mol["n_mol"], dv = intrinsic_line_width)

            # Spectrum creation/calc
            
            


            print (f"Molecule Initialized: {mol_name}")

    


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





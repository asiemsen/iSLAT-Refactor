from iSLAT_Refactor.app_globals import INITIAL_PARAMETERS, DEFAULT_INITIAL_PARAMS
from ir_model.moldata import MolData

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

            self.moleculeDictionary[molName]["data"] = MolData(mol_name, mol_filepath)
            self.moleculeDictionary[molName]["scale_exponent"] = scale_exponent
            self.moleculeDictionary[molName]["scale_number"] = scale_number
            self.moleculeDictionary[molName]["t_kin"] = t_kin
            self.moleculeDictionary[molName]["radius_init"] = radius_init
            self.moleculeDictionary[molName]["n_mol_init"] = n_mol_init

            print (f"Molecule Initialized: {mol_name}")

    








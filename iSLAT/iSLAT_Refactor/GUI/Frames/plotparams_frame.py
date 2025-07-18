import tkinter as tk
from tkinter import ttk

from iSLAT_Refactor import app_globals
from ..tool_frame import ToolFrame
from iSLAT_Refactor.core.frame_functions import plotparam_functions


class PlotParamsFrame(ToolFrame): 
    def build(self):

        # Create and place the xp1 text box in row 12, column 0
        self.xp1_label = tk.Label(self, text="Plot start:")
        self.xp1_label.grid(row=0, column=0)
        self.xp1_entry = tk.Entry(self, width=8)
        self.xp1_entry.insert(0, str(app_globals.xp1))
        self.xp1_entry.grid(row=0, column=1)

        # Create and place the rng text box in row 12, column 2
        self.rng_label = tk.Label(self, text="Plot range:")
        self.rng_label.grid(row=0, column=2)
        self.rng_entry = tk.Entry(self, width=8)
        self.rng_entry.insert(0, str(app_globals.rng))
        self.rng_entry.grid(row=0, column=3)


        # Create and place the min_lamb text box in row 2, column 0
        self.min_lamb_label = tk.Label(self, text="Min. Wave:")
        self.min_lamb_label.grid(row=1, column=0)
        self.min_lamb_entry = tk.Entry(self, width=8)
        self.min_lamb_entry.insert(0, str(app_globals.min_lamb))
        self.min_lamb_entry.grid(row=1, column=1)

        # Create and place the max_lamb text box in row 2, column 2
        self.max_lamb_label = tk.Label(self, text="Max. Wave:")
        self.max_lamb_label.grid(row=1, column=2)
        self.max_lamb_entry = tk.Entry(self, width=8)
        self.max_lamb_entry.insert(0, str(app_globals.max_lamb))
        self.max_lamb_entry.grid(row=1, column=3)

        # Create and place the dist text box in row 3, column 0
        self.dist_label = tk.Label(self, text="Distance:")
        self.dist_label.grid(row=2, column=0)
        self.dist_entry = tk.Entry(self, width=8)
        self.dist_entry.insert(0, str(app_globals.dist))
        self.dist_entry.grid(row=2, column=1)

        # Create and place the RV text box in row 3, column 0
        self.dist_label = tk.Label(self, text="Stellar RV:")
        self.dist_label.grid(row=2, column=2)
        self.star_rv_entry = tk.Entry(self, width=8)
        self.star_rv_entry.insert(0, str(app_globals.star_rv))
        self.star_rv_entry.grid(row=2, column=3)

        # Create and place the fwhm text box in row 3, column 2
        self.fwhm_label = tk.Label(self, text="FWHM:")
        self.fwhm_label.grid(row=3, column=0)
        self.fwhm_entry = tk.Entry(self,  width=8)
        self.fwhm_entry.insert(0, str(app_globals.fwhm))
        self.fwhm_entry.grid(row=3, column=1)

        # Create and place the fwhm text box in row 3, column 2
        self.intrinsic_line_width_label = tk.Label(self, text="Broadening:")
        self.intrinsic_line_width_label.grid(row=3, column=2)
        self.intrinsic_line_width_entry = tk.Entry(self,  width=8)
        self.intrinsic_line_width_entry.insert(0, str(app_globals.intrinsic_line_width))
        self.intrinsic_line_width_entry.grid(row=3, column=3)

        # Create and place the xp1 text box in row 12, column 0
        self.specsep_label = tk.Label(self, text="Line Separ.:")
        #specsep_label.grid(row=4, column=2, pady=(0, 45))
        self.specsep_label.grid(row=4, column=2)
        self.specsep_entry = tk.Entry(self, width=8)
        self.specsep_entry.insert(0, str(app_globals.specsep))
        #specsep_entry.grid(row=4, column=3, pady=(0, 45))
        self.specsep_entry.grid(row=4, column=3)

        # Create a dropdown menu in the new window
        molNames = self.controller.moleculeManager.moleculeDictionary.keys()
        self.spanselectlab = tk.Label(self, text="Molecule:")
        #spanselectlab.grid(row=4, column=0, pady=(0, 45))
        self.spanselectlab.grid(row=4, column=0)
        self.spanoptionsvar = [name.upper() for name in molNames]
        self.spandropdowntext = tk.StringVar()
        self.spandropd = ttk.Combobox(self, textvariable=self.spandropdowntext, values=self.spanoptionsvar, width=6)
        self.spandropd.set(self.spanoptionsvar[0])
        #spandropd.grid(row=4, column=1, pady=(0, 45))
        self.spandropd.grid(row=4, column=1)
 
    def configureButtons(self, appController):
        self.xp1_entry.bind("<Return>", lambda event, attr = "xp1": 
                            plotparam_functions.update_xp1_rng(self, attr, appController))
        
        self.rng_entry.bind("<Return>", lambda event, attr = "rng": 
                            plotparam_functions.update_xp1_rng(self, attr, appController))
        
        self.min_lamb_entry.bind("<Return>", lambda event, attr = "min_lamb": 
                            plotparam_functions.updateSpectrum(self, attr, appController))
        
        self.max_lamb_entry.bind("<Return>", lambda event, attr = "max_lamb": 
                            plotparam_functions.updateSpectrum(self, attr, appController))
        
        self.dist_entry.bind("<Return>", lambda event, attr = "dist": 
                            plotparam_functions.dist_submit(self, appController))
        
        self.star_rv_entry.bind("<Return>", lambda event, attr = "star_rv": 
                            plotparam_functions.stellar_submit(self, appController))
        
        self.fwhm_entry.bind("<Return>", lambda event, attr = "fwhm": 
                            plotparam_functions.generic_submit(self, appController))
        
        self.intrinsic_line_width_entry.bind("<Return>", lambda event, attr = "broadening": 
                            plotparam_functions.generic_submit(self, appController))

        
        



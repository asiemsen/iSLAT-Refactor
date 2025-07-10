import tkinter as tk

from ..tool_frame import ToolFrame

class FunctionsFrame(ToolFrame):
    def build(self):

        self.save_button = tk.Button(self, text="Save Line", width=13, height=1)
        self.save_button.grid(row=0, column=0)

        self.fit_button = tk.Button(self, text="Fit Line", width=13, height=1)
        self.fit_button.grid(row=0, column=1)

        self.savedline_button = tk.Button(self, text="Show Saved Lines", width=13, height=1) #  command=print_saved_lines, width=13, height=1)                 
        self.savedline_button.grid(row=1, column=0)

        fitsavedline_button = tk.Button(self, text="Fit Saved Lines", width=13, height=1) # command=fit_saved_lines, width=13, height=1)        
        fitsavedline_button.grid(row=1, column=1)

        self.autofind_button = tk.Button(self, text="Find Single Lines", width=13, height=1) # command=single_finder, width=13, height=1)
        self.autofind_button.grid(row=2, column=0)

        self.atomlines_button = tk.Button(self, text='Show Atomic Lines', width=13, height=1) # command=lambda: print_atomic_lines(), width=13, height=1)                              
        self.atomlines_button.grid(row=2, column=1)

        slabfit_button = tk.Button(self, text='Single Slab Fit', width=13, height=1) # command=lambda: run_slabfit(), width=13, height=1)             
        slabfit_button.grid(row=3, column=0)

        deblender_button = tk.Button(self, text='Line De-blender', width=13, height=1) #  command=lambda: fitmulti_onselect(), width=13, height=1)        
        deblender_button.grid(row=3, column=1)


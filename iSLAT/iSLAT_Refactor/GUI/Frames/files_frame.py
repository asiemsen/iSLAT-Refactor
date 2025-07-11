import tkinter as tk

from iSLAT_Refactor import app_globals
from ..tool_frame import ToolFrame

class FilesFrame(ToolFrame):
    # Configure columns to expand and fill the width
    def build(self):
        for i in range(5):
            self.columnconfigure(i, weight=1)
        # Space Labels
        self.specfile_label = tk.Label(self, text = 'Spectrum Data File:')
        self.specfile_label.grid(row=0, column=0, columnspan=2, stick='nsew')

        self.linefile_label = tk.Label(self, text='Input Line List:')
        self.linefile_label.grid(row=2, column=0, columnspan=2, sticky='nsew')

        self.output_label = tk.Label(self, text='Output Line Measurements:')
        self.output_label.grid(row=4, column=0, columnspan=2, sticky='nsew')  # Center-align using grid

        # Boxes for files 
        self.specfile_box = tk.Frame(self, relief='solid', borderwidth=1)
        self.specfile_box.grid(row=1, column=0, columnspan=2, sticky='nesw', padx=4)

        self.spec_box_label = tk.Label(self.specfile_box, text=str(app_globals.file_name), anchor='center', justify='center')
        self.spec_box_label.grid(row=0, column=0, sticky='nsew')

        self.specfile_box.grid_rowconfigure(0, weight=1)
        self.specfile_box.grid_columnconfigure(0, weight=1)

        # Boxes for files 
        self.linefile_box = tk.Frame(self, relief='solid', borderwidth=1)
        self.linefile_box.grid(row=3, column=0, columnspan=2, sticky='nesw', padx=4)

        self.lf_box_label = tk.Label(self.linefile_box, text="", anchor='center', justify='center')
        self.lf_box_label.grid(row=0, column=0, sticky='nsew')

        self.linefile_box.grid_rowconfigure(0, weight=1)
        self.linefile_box.grid_columnconfigure(0, weight=1)

        # Boxes for files 
        self.output_box = tk.Frame(self, relief='solid', borderwidth=1)
        self.output_box.grid(row=5, column=0, columnspan=2, sticky='nesw', padx=4)

        self.output_box_label = tk.Label(self.output_box, text="", anchor='center', justify='center')
        self.output_box_label.grid(row=0, column=0, sticky='nesw')

        self.output_box.grid_rowconfigure(0, weight=1)
        self.output_box.grid_columnconfigure(0, weight=1)


        #Column 2 buttons

        self.file_button = tk.Button(self, text='Open File') #, command=selectfile
        self.file_button.grid(row=1, column=2)

        self.linefile_button = tk.Button(self, text='Open File') #, command=selectlinefile
        self.linefile_button.grid(row=3, column=2)

        self.linesave_button = tk.Button(self, text='Define File')# , command=savelinefile
        self.linesave_button.grid(row=5, column=2)






        
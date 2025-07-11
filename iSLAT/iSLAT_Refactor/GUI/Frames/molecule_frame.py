import tkinter as tk

from ..tool_frame import ToolFrame

class MoleculeFrame(ToolFrame):

    def build(self):
        # Create a canvasscroll widget
        self.canvasscroll = tk.Canvas(self)
        self.canvasscroll.grid(row=0, column=0, sticky="nsew")

        # Create vertical and horizontal scrollbar widgets and associate them with the canvasscroll
        self.vscrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvasscroll.yview)
        self.vscrollbar.grid(row=0, column=1, sticky="ns")
        self.hscrollbar = tk.Scrollbar(self, orient="horizontal", command=self.canvasscroll.xview)
        self.hscrollbar.grid(row=1, column=0, columnspan= 2, sticky="ew")

        # Configure the canvasscroll to use the scrollbars
        self.canvasscroll.configure(yscrollcommand=self.vscrollbar.set, xscrollcommand=self.hscrollbar.set)

        # Allow resizing of the canvasscroll and outer_frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create the frame that will contain your actual content
        self.data_frame = tk.Frame(self.canvasscroll, borderwidth=2)  # , relief="groove")
        self.canvasscroll.create_window((0, 0), window=self.data_frame, anchor="nw")

        self.data_frame.bind("<Configure>", self.on_frame_configure)

        # Create labels for columns
        for col, label in enumerate(self.controller.column_labels):
            label_widget = tk.Label(self.data_frame, text=label)
            label_widget.grid(row=0, column=col)
        
        self.createInputFields(self.controller.moleculeManager.moleculeDictionary)

        
    def createInputFields(self, moleculeDictionary):

        self.inputFields = {}

        for row, mol_name in enumerate(moleculeDictionary):
            row += 1
            params = moleculeDictionary[mol_name]
            scale_exponent = params["scale_exponent"]
            scale_number = params["scale_number"]
            t_kin = params["t_kin"]
            radius_init = params["radius"]
            n_mol_init = params["n_mol"]

            self.inputFields[mol_name] = {}
            inFields = self.inputFields[mol_name]

            # row label 
            inFields["rowl"] = tk.Entry(self.data_frame, width=6)
            inFields["rowl"].grid(row = row, column = 0)
            inFields["rowl"].insert(0, mol_name.upper())

            #Temperature Input Field
            inFields["temp"] = tk.Entry(self.data_frame, width =4)
            inFields["temp"].grid(row=row, column = 1)
            inFields["temp"].insert(0, t_kin)

            # Radius input field 
            inFields["radius"] = tk.Entry(self.data_frame, width=4)
            inFields["radius"].grid(row=row, column =2)
            inFields["radius"].insert(0, radius_init)

            # Col density input field 
            inFields["density"] = tk.Entry(self.data_frame, width=6)
            inFields["density"].grid(row=row, column=3)
            inFields["density"].insert(0, f"{n_mol_init:.{1}e}")

            # Visibility Checkbutton
            inFields["vis_button"] = tk.Checkbutton(self.data_frame, 
                                                        text='', 
                                                        )
            if mol_name == 'h2o':
                inFields["vis_button"].select()

            inFields["vis_button"].grid(row=row, column=4)

            # Delete Button
            inFields["delete"] = tk.Button(self.data_frame, text="X")
            inFields["delete"].grid(row=row, column=5)

            # Color Button 
            inFields["color"] = tk.Button(self.data_frame, text=" ", background=self.controller.moleculeManager.moleculeDictionary[mol_name]["color"])
            inFields["color"].grid(row=row, column=6)
                
    # # Configure the canvasscroll scroll region
    def on_frame_configure(self, event):
        self.canvasscroll.configure(scrollregion=self.canvasscroll.bbox("all"))

    def update_button_colors(self, moleculeDictionary):
        for molName in moleculeDictionary:
            self.inputFields[molName]["color"].config(bg = moleculeDictionary[molName]["color"])

    def configureButton(self, moleculeDictionary, plot1, canvas):
        for molName in moleculeDictionary:
            self.inputFields[molName]["vis_button"].configure(command=lambda mn = molName, ax1 = plot1, can = canvas:self.controller.moleculeManager.toggle_visible(mn, ax1, canvas))






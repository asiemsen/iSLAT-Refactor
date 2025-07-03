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
        data_frame = tk.Frame(self.canvasscroll, borderwidth=2)  # , relief="groove")
        self.canvasscroll.create_window((0, 0), window=self.data_frame, anchor="nw")

        self.data_frame.bind("<Configure>", self.on_frame_configure)

        


    # # Configure the canvasscroll scroll region
    def on_frame_configure(self, event):
        self.canvasscroll.configure(scrollregion=self.canvasscroll.bbox("all"))



import tkinter as tk

class ToolFrame(tk.Frame):
    def __init__(self, parent, controller = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.build()

    def build():
        pass
    


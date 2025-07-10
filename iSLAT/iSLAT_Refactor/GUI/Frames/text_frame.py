import tkinter as tk

from ..tool_frame import ToolFrame

class TextFrame(ToolFrame):
    def build(self):
        self.data_field = tk.Text(self, wrap='word', height=13, width=24)
        self.data_field.pack(fill='both', expand=True)


#new entry point for iSLAT
import tkinter as tk

from core.core import selectfileinit


root = tk.Tk ()
root.withdraw ()
root.call ('wm', 'attributes', '.', '-topmost', True)


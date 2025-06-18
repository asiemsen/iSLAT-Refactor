#new entry point for iSLAT
import tkinter as tk

from mixed.mixed import selectfileinit
from core.core import read_from_user_csv

root = tk.Tk ()
root.withdraw ()
root.call ('wm', 'attributes', '.', '-topmost', True)

selectfileinit()

print (' ')
print ('Loading molecule files: ...')

molecules_data = read_from_user_csv()

#MAKE CONSTANT CLASS TO IMPORT




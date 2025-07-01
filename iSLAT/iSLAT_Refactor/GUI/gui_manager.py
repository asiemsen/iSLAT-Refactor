import tkinter as tk
import matplotlib.pyplot as plt

from iSLAT_Refactor import app_globals
from matplotlib.gridspec import GridSpec

class GUI_Manager:

    def __init__(self, root) -> None:
        self.mode = False 
        self.background = 'white'
        self.foreground = 'black'

        self.iSLAT_version = "Refactor Build"

        self.root = tk.Tk()
        

    def init_window(self) -> None:
        self.root.withdraw()

        self.root.call ('wm', 'attributes', '.', '-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

        self.root.title("iSLAT " + self.iSLAT_version)

        self.root.geometry("1200x800")
        self.root.after(100, self.root.deiconify)

    def build_layout(self) -> None:
        plt.rcParams['font.size'] = 10
        # Creating the graph
        self.fig = plt.figure(figsize=(15, 8.5))
        # fig = plt.figure()
        self.gs = GridSpec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1, 1.5])
        

    def initialize_graphs(self) -> None:
        self.ax1 = self.fig.add_subplot (self.gs[0, :])
        self.ax2 = self.fig.add_subplot (self.gs[1, 0])
        self.ax3 = self.fig.add_subplot (self.gs[1, 1])

        self.ax1.set_ylabel('Flux density (Jy)')
        self.ax1.set_xlim(xmin=app_globals.xp1, xmax=app_globals.xp2)
        self.data_line, = self.ax1.plot(app_globals.wave_data, app_globals.flux_data, color=self.foreground, linewidth=1)
        self.data_line.set_label('Data')
        self.ax1.legend()
        

        self.ax2.set_xlabel('Wavelength (μm)')
        self.ax2.set_ylabel('Flux density (Jy)')

        
        
        




        

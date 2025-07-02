import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np

from iSLAT_Refactor import app_globals
from matplotlib.gridspec import GridSpec

class GUI_Manager:

    def __init__(self, root) -> None:
        # for dark mode
        self.mode = False 
        self.background = 'white'
        self.foreground = 'black'

        self.iSLAT_version = "Refactor Build"

        self.num_rows = 9

        # Calculate the height and width of each row
        self.row_height = 0.035
        self.row_width = 0.19

        # Calculate the total height of all rows
        self.total_height = self.row_height * self.num_rows

        # Calculate the starting y-position for the first row within the control_border
        self.start_y = 0.52 + (0.45 - self.total_height) / 2  # Center vertically

        # Define the column labels
        self.column_labels = ['Molecule', 'Temp.', 'Radius', 'Col. Dens', 'On', 'Del.', 'Color']

        # Create a dictionary to store the visibility buttons
        self.vis_buttons_dict = {}

        self.nb_of_columns = 10  # to be replaced by the relevant number

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

        self.gs = GridSpec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1, 1.5])

        self.fig.subplots_adjust (left=0.06, right=0.97, top=0.97, bottom=0.09)

        # create buttons for top of GUI
        self.title_frame = tk.Frame(self.root, bg="gray")
        self.title_frame.grid(row=0, column=0, columnspan= self.nb_of_columns, sticky='ew')

        # Create a frame to hold the canvasscroll and both scrollbars
        outer_frame = tk.Frame(self.root)
        outer_frame.grid(row=self.title_frame.grid_info()['row'] + self.title_frame.grid_info()['rowspan'], column=0, rowspan=10,
                        columnspan=5, sticky="nsew")
        
        # Create a canvasscroll widget
        self.canvasscroll = tk.Canvas(outer_frame)
        self.canvasscroll.grid(row=0, column=0, sticky="nsew")

        # Create vertical and horizontal scrollbar widgets and associate them with the canvasscroll
        vscrollbar = tk.Scrollbar(self.outer_frame, orient="vertical", command=self.canvasscroll.yview)
        vscrollbar.grid(row=0, column=1, sticky="ns")
        hscrollbar = tk.Scrollbar(outer_frame, orient="horizontal", command=self.canvasscroll.xview)
        hscrollbar.grid(row=1, column=0, sticky="ew")
        

    def initialize_graphs(self) -> None:
        self.ax1 = self.fig.add_subplot (self.gs[0, :])
        self.ax2 = self.fig.add_subplot (self.gs[1, 0])
        self.ax3 = self.fig.add_subplot (self.gs[1, 1])

        self.ax1.set_ylabel('Flux density (Jy)')
        self.ax1.set_xlim(xmin=app_globals.xp1, xmax=app_globals.xp2)
        self.data_line, = self.ax1.plot(app_globals.wave_data, app_globals.flux_data, color=self.foreground, linewidth=1)
        self.data_line.set_label('Data')
        self.ax1.legend()

        self.size_graph(self.ax1, app_globals.xp1, app_globals.xp2)
        

        self.ax2.set_xlabel('Wavelength (μm)')
        self.ax2.set_ylabel('Flux density (Jy)')
        self.ax2.set_frame_on (False)

        # make empty lines for the second plot
        self.ax2.set_title ('Line inspection plot', fontsize='medium')
        self.data_line_select, = self.ax2.plot([], [], color=self.foreground, linewidth=1)

        self.ax3.set_frame_on (False)

    def size_graph(self, ax, xp1, xp2) -> None:
        # Scaling the y-axis based on tallest peak of data
        range_flux_cnts = app_globals.input_spectrum_data[(app_globals.input_spectrum_data['wave'] > app_globals.xp1) & (app_globals.input_spectrum_data['wave'] < app_globals.xp2)]
        range_flux_cnts.index = range (len(range_flux_cnts.index))
        fig_height = np.nanmax(range_flux_cnts.flux)
        fig_bottom_height = np.min(range_flux_cnts.flux)
        ax.set_ylim(ymin=fig_bottom_height, ymax=fig_height + (fig_height / 8))


        
        
        




        

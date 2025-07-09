import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np

from iSLAT_Refactor import app_globals
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_tkagg import(FigureCanvasTkAgg, NavigationToolbar2Tk)

from .Frames.molecule_frame import MoleculeFrame
from .Frames.files_frame import FilesFrame
from .Frames.plotparams_frame import PlotParamsFrame

class GUI_Manager:

    def __init__(self, window, moleculeManager) -> None:
        # for dark mode
        self.moleculeManager = moleculeManager
        self.root = window
        self.mode = False 
        self.BG = 'lightgray'
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

        # self.root = tk.Tk()



        self.init_window()
        self.build_layout()
        self.initialize_graphs()
        
        # Grid resizing
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=0)  # Frame manager column
        self.root.grid_columnconfigure(1, weight=1)  # Canvas column
            

    def init_window(self) -> None:
        self.root.withdraw()

        self.root.call ('wm', 'attributes', '.', '-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

        self.root.title("iSLAT " + self.iSLAT_version)

        # self.root.geometry("1200x800")
        self.root.deiconify()
        # self.root.after(100, self.root.deiconify)

    def build_layout(self) -> None:
        plt.rcParams['font.size'] = 10
        # Creating the graph
        self.fig = plt.figure(figsize=(15, 8.5))
        # Create a FigureCanvasTkAgg widget to embed the figure in the tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=1, sticky='nsew')

        self.gs = GridSpec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1, 1.5])

        self.fig.subplots_adjust(left=0.06, right=0.97, top=0.97, bottom=0.09)

        self.createTitleFrame()

        # create buttons for top of GUI
        self.frame_manager = tk.Frame(self.root, relief='groove', bg='red')
        self.frame_manager.grid(row = 1, column = 0, sticky='nsew')
        self.frame_manager.grid_columnconfigure(0, weight=0)

        # Add molecule frmae
        self.molecule_frame = MoleculeFrame(parent=self.frame_manager, controller = self, relief='groove')
        self.molecule_frame.grid(row=0, column=0, sticky = 'new')
        self.frame_manager.grid_rowconfigure(0, weight=0)
        
        # Add files frame
        self.files_frame = FilesFrame(parent=self.frame_manager, controller= self, relief='groove')
        self.files_frame.grid(row=1, column=0, sticky='new')
        self.frame_manager.grid_rowconfigure(1, weight=0)

        # Add plot params frame
        self.plotparams_frame = PlotParamsFrame(parent=self.frame_manager, controller=self, relief='groove')
        self.plotparams_frame.grid(row=2, column=0, sticky='new')
        self.plotparams_frame.grid_rowconfigure(1, weight=0)


        

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
        self.ax2.set_frame_on(False)
        # self.ax2.set_title('Line inspection plot', fontsize='medium')
        self.data_line_select, = self.ax2.plot([], [], color=self.foreground, linewidth=1)

        # make empty lines for the second plot
        self.ax2.set_title ('Line inspection plot', fontsize='medium')
        self.data_line_select, = self.ax2.plot([], [], color=self.foreground, linewidth=1)

        self.ax3.set_frame_on (False)

        # adjust the plots to make room for the widgets
        self.fig.subplots_adjust(left=0.06, right=0.97, top=0.97, bottom=0.09)


    def size_graph(self, ax, xp1, xp2) -> None:
        # Scaling the y-axis based on tallest peak of data
        range_flux_cnts = app_globals.input_spectrum_data[(app_globals.input_spectrum_data['wave'] > xp1) & (app_globals.input_spectrum_data['wave'] < xp2)]
        range_flux_cnts.index = range (len(range_flux_cnts.index))
        fig_height = np.nanmax(range_flux_cnts.flux)
        fig_bottom_height = np.min(range_flux_cnts.flux)
        ax.set_ylim(ymin=fig_bottom_height, ymax=fig_height + (fig_height / 8))


    def createTitleFrame(self) -> None:

        self.tf_nextCol = 0

        self.title_frame = tk.Frame(self.root, bg="lightgrey")
        self.title_frame.grid(row=0, column=0, columnspan= 2, sticky='ew')

        # Create title frame buttons
        buttons_info = [
            ("HITRAN query", 'lightgray', 'gray'), # , self.import_molecule
            ('Default Molecules', 'lightgray', 'gray'), #, self.load_default_molecules
            ('Add Molecule', 'lightgray', 'gray'), # , self.add_molecule
            ('Save Parameters', 'lightgray', 'gray'), # , self.save_params
            ('Load Parameters', 'lightgray', 'gray'), # , self.load_params
            ('Export Models', 'lightgray', 'gray'), # , self.export_models
            ('Toggle Legend', 'lightgray', 'gray'),
        ]

        self.title_frame_buttons = {}

        for column, (text, bg, activebg) in enumerate(buttons_info):
            button = tk.Button(self.title_frame, text=text, bg = bg, activebackground=activebg)
            button.grid(row = 0, column= column)
            self.title_frame_buttons[text] = button
            self.tf_nextCol += 1

        # Create title frame toolbar
        toolbar_frame = tk.Frame(self.title_frame)
        toolbar_frame.grid(row=0, column=self.tf_nextCol, sticky="nsew")  # Place the frame in row 0, column 9
        # Create a toolbar and update it
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        self.title_frame.grid_columnconfigure(self.tf_nextCol, weight=1)
        self.tf_nextCol += 1



    def addButton(self, frame, **kwargs) -> tk.Button:
        
        button = tk.Button(frame, **kwargs)


        






        

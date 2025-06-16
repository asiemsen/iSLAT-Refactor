# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

root = tk.Tk()
root.withdraw()
root.call('wm', 'attributes', '.', '-topmost', True)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

if mode:
    global background
    global foreground

    # plt.style.use('dark_background')
    # Set Matplotlib rcParams for dark background
    matplotlib.rcParams['figure.facecolor'] = 'black'
    matplotlib.rcParams['axes.facecolor'] = 'black'
    matplotlib.rcParams['axes.edgecolor'] = 'white'
    matplotlib.rcParams['xtick.color'] = 'white'
    matplotlib.rcParams['ytick.color'] = 'white'
    matplotlib.rcParams['text.color'] = 'white'
    matplotlib.rcParams['axes.labelcolor'] = 'white'
    background = 'black'
    foreground = 'white'
    # self.toolbar.setStyleSheet("background-color:Gray;")
else:

    background = 'white'
    foreground = 'black'


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
# Creating the graph
fig = plt.figure(figsize=(15, 8.5))
# fig = plt.figure()
gs = GridSpec(nrows=2, ncols=2, width_ratios=[1, 1], height_ratios=[1, 1.5])
ax1 = fig.add_subplot(gs[0, :])
ax2 = fig.add_subplot(gs[1, 0])
ax3 = fig.add_subplot(gs[1, 1])

# Create a text box for streaming useful information in the third section
# text_box = fig.add_subplot(gs[1, 0])  # This is the third section
# text_box_data = TextBox(text_box, label='', color = background, hovercolor= background)
# ax3.set_ylabel(r'ln(4πF/(hν$A_{u}$$g_{u}$))')
# ax3.set_xlabel(r'$E_{u}$')
ax2.set_xlabel('Wavelength (μm)')
ax1.set_ylabel('Flux density (Jy)')
ax2.set_ylabel('Flux density (Jy)')
ax1.set_xlim(xmin=xp1, xmax=xp2)
plt.rcParams['font.size'] = 10
data_line, = ax1.plot(wave_data, flux_data, color=foreground, linewidth=1)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

for mol_name, mol_filepath, mol_label in molecules_data:
    molecule_name_lower = mol_name.lower()

    if molecule_name_lower == 'h2o':
        exec(
            f"{molecule_name_lower}_line, = ax1.plot({molecule_name_lower}_spectrum.lamgrid, fluxes_{molecule_name_lower}, alpha=0.8, linewidth=1)",
            globals())
    else:
        exec(f"{molecule_name_lower}_line, = ax1.plot([], [], alpha=0.8, linewidth=1)", globals())
    exec(f"{molecule_name_lower}_line.set_label('{mol_label}')", globals())

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
data_line.set_label('Data')
sum_line, = ax1.plot([], [], color='purple', linewidth=1)
sum_line.set_label('Sum')
ax1.legend()

ax2.set_frame_on(False)
ax3.set_frame_on(False)

# make empty lines for the second plot
ax2.set_title('Line inspection plot', fontsize='medium')
data_line_select, = ax2.plot([], [], color=foreground, linewidth=1)

# Scaling the y-axis based on tallest peak of data
range_flux_cnts = input_spectrum_data[(input_spectrum_data['wave'] > xp1) & (input_spectrum_data['wave'] < xp2)]
range_flux_cnts.index = range(len(range_flux_cnts.index))
fig_height = np.nanmax(range_flux_cnts.flux)
fig_bottom_height = np.min(range_flux_cnts.flux)
ax1.set_ylim(ymin=fig_bottom_height, ymax=fig_height + (fig_height / 8))

# adjust the plots to make room for the widgets
fig.subplots_adjust(left=0.06, right=0.97, top=0.97, bottom=0.09)

# Populating the population diagram graph
pop_diagram()

num_rows = 9

# Calculate the height and width of each row
row_height = 0.035
row_width = 0.19

# Calculate the total height of all rows
total_height = row_height * num_rows

# Calculate the starting y-position for the first row within the control_border
start_y = 0.52 + (0.45 - total_height) / 2  # Center vertically

# Define the column labels
column_labels = ['Molecule', 'Temp.', 'Radius', 'Col. Dens', 'On', 'Del.', 'Color']

# Create a dictionary to store the visibility buttons
vis_buttons_dict = {}

# Create a tkinter window
window = tk.Tk()
window.title("iSLAT " + iSLAT_version)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

"""
# MENU of tkinter GUI frame parts and definitions:
# title_frame : menu at the top of the GUI (Add molecule, etc)
# molecule_frame (contained by outer_frame) : top right frame for molecules and their parameters (temp, rad, coldens)
# files_frame : file input and output
# plotparams_frame : plot parameters (plot start, range, etc)
# functions_frame : buttons to activate functions (Save line, Fit line, etc)
# text_frame : bottom right empty frame for text messages
"""

# create buttons for top of GUI
nb_of_columns = 10  # to be replaced by the relevant number
title_frame = tk.Frame(window, bg="gray")
title_frame.grid(row=0, column=0, columnspan=nb_of_columns, sticky='ew')

# Create a frame to hold the canvasscroll and both scrollbars
outer_frame = tk.Frame(window)
outer_frame.grid(row=title_frame.grid_info()['row'] + title_frame.grid_info()['rowspan'], column=0, rowspan=10,
                 columnspan=5, sticky="nsew")

# Create a canvasscroll widget
canvasscroll = tk.Canvas(outer_frame)
canvasscroll.grid(row=0, column=0, sticky="nsew")

# Create vertical and horizontal scrollbar widgets and associate them with the canvasscroll
vscrollbar = tk.Scrollbar(outer_frame, orient="vertical", command=canvasscroll.yview)
vscrollbar.grid(row=0, column=1, sticky="ns")
hscrollbar = tk.Scrollbar(outer_frame, orient="horizontal", command=canvasscroll.xview)
hscrollbar.grid(row=1, column=0, sticky="ew")

# Configure the canvasscroll to use the scrollbars
canvasscroll.configure(yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)

# Allow resizing of the canvasscroll and outer_frame
outer_frame.grid_rowconfigure(0, weight=1)
outer_frame.grid_columnconfigure(0, weight=1)

# Create the frame that will contain your actual content
molecule_frame = tk.Frame(canvasscroll, borderwidth=2)  # , relief="groove")
canvasscroll.create_window((0, 0), window=molecule_frame, anchor="nw")


# Configure the canvasscroll scroll region
def on_frame_configure(event):
    canvasscroll.configure(scrollregion=canvasscroll.bbox("all"))


molecule_frame.bind("<Configure>", on_frame_configure)

# Create the frame with the specified properties
# molecule_frame = tk.Frame(window, borderwidth=2, relief="groove")
# molecule_frame.grid(row=1, column=0, rowspan=10, columnspan=5, sticky="nsew")

# Create labels for columns
for col, label in enumerate(column_labels):
    label_widget = tk.Label(molecule_frame, text=label)
    label_widget.grid(row=0, column=col)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

# Loop to create rows of input fields and buttons for each chemical
nextrow = 1  # Start with row 1
for row, (mol_name, mol_filepath, mol_label) in enumerate(molecules_data):
    # global nextrow
    y_row = start_y + row_height * (num_rows - row - 1)
    row = row + 1
    # Get the initial values for the current chemical from the dictionary
    params = initial_values[mol_name.lower()]
    scale_exponent = params["scale_exponent"]
    scale_number = params["scale_number"]
    t_kin = params["t_kin"]
    radius_init = params["radius_init"]
    n_mol_init = params["n_mol_init"]

    # Row label
    exec(f"{mol_name.lower()}_rowl_field = tk.Entry(molecule_frame, width=6)")
    eval(f"{mol_name.lower()}_rowl_field").grid(row=row, column=0)
    eval(f"{mol_name.lower()}_rowl_field").insert(0, f"{mol_name}")

    # Temperature input field
    exec(f"{mol_name.lower()}_temp_field = tk.Entry(molecule_frame, width=4)")
    eval(f"{mol_name.lower()}_temp_field").grid(row=row, column=1)
    eval(f"{mol_name.lower()}_temp_field").insert(0, f"{t_kin}")
    eval(f"{mol_name.lower()}_temp_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
        f"{mol_name.lower()}_temp_field"]: submit_temp(ce.get(), mn))

    CreateToolTip(eval(f"{mol_name.lower()}_temp_field"), text='Excitation temperature\n'
                                                               'units: K')

    # Radius input field
    exec(f"{mol_name.lower()}_rad_field = tk.Entry(molecule_frame, width=4)")
    eval(f"{mol_name.lower()}_rad_field").grid(row=row, column=2)
    eval(f"{mol_name.lower()}_rad_field").insert(0, f"{radius_init}")
    eval(f"{mol_name.lower()}_rad_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
        f"{mol_name.lower()}_rad_field"]: submit_rad(ce.get(), mn))

    CreateToolTip(eval(f"{mol_name.lower()}_rad_field"), text='Equivalent radius\n'
                                                              'units: au')

    # Column Density input field
    exec(f"{mol_name.lower()}_dens_field = tk.Entry(molecule_frame, width=6)")
    eval(f"{mol_name.lower()}_dens_field").grid(row=row, column=3)
    eval(f"{mol_name.lower()}_dens_field").insert(0, f"{n_mol_init:.{1}e}")
    eval(f"{mol_name.lower()}_dens_field").bind("<Return>", lambda event, mn=mol_name.lower(), ce=globals()[
        f"{mol_name.lower()}_dens_field"]: submit_col(ce.get(), mn))

    CreateToolTip(eval(f"{mol_name.lower()}_dens_field"), text='Column density\n'
                                                               'units: cm^(-2)')

    # Visibility Checkbutton
    if mol_name.lower() == 'h2o':
        exec(f"{mol_name.lower()}_vis_status = tk.BooleanVar()")
        exec(f"{mol_name.lower()}_vis_status.set(True)")  # Set the initial state
        exec(
            f"{mol_name.lower()}_vis_checkbutton = tk.Checkbutton(molecule_frame, text='', variable={mol_name.lower()}_vis_status, onvalue=True, offvalue=False, command=lambda mn=mol_name.lower(): model_visible(mn))")
        exec(f"{mol_name.lower()}_vis_checkbutton.select()")
    else:
        globals()[f"{mol_name.lower()}_vis_status"] = tk.BooleanVar()
        globals()[f"{mol_name.lower()}_vis_checkbutton"] = tk.Checkbutton(molecule_frame, text='', variable=eval(
            f"{mol_name.lower()}_vis_status"), command=lambda mn=mol_name.lower(): model_visible(mn))
        globals()[f"{mol_name.lower()}_vis_status"].set(False)  # Set the initial state

    eval(f"{mol_name.lower()}_vis_checkbutton").grid(row=row, column=4)

    CreateToolTip(eval(f"{mol_name.lower()}_vis_checkbutton"), text='Turn on/off this\n'
                                                                    'model in the plot')

    # Delete button
    del_button = tk.Button(molecule_frame, text="X",
                           command=lambda widget=eval(f"{mol_name.lower()}_rowl_field"): delete_row(widget))
    del_button.grid(row=row, column=5)

    CreateToolTip(del_button, text='Remove this model\n'
                                   'from the GUI')

    color_button = tk.Button(molecule_frame, text=" ",
                             command=lambda widget=eval(f"{mol_name.lower()}_rowl_field"): choose_color(widget))
    color_button.grid(row=row, column=6)

    CreateToolTip(color_button, text='Change color\n'
                                     'for this model')

    nextrow = row + 1

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

files_frame = tk.Frame(window, borderwidth=2, relief="groove")
files_frame.grid(row=outer_frame.grid_info()['row'] + outer_frame.grid_info()['rowspan'], column=0, rowspan=7,
                 columnspan=5, sticky="nsew")

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------


# Configure columns to expand and fill the width
for i in range(5):
    files_frame.columnconfigure(i, weight=1)

# Create a frame to hold the box outline
box_frame = tk.Frame(files_frame)
box_frame.grid(row=1, column=0, columnspan=5, sticky='nsew')

specfile_label = tk.Label(files_frame, text='Spectrum Data File:')
specfile_label.grid(row=0, column=0, columnspan=5, sticky='nsew')  # Center-align using grid

linefile_label = tk.Label(files_frame, text='Input Line List:')
linefile_label.grid(row=2, column=0, columnspan=5, sticky='nsew')  # Center-align using grid

linefile_label = tk.Label(files_frame, text='Output Line Measurements:')
linefile_label.grid(row=4, column=0, columnspan=5, sticky='nsew')  # Center-align using grid

# Create a frame to hold the box outline
linebox_frame = tk.Frame(files_frame)
linebox_frame.grid(row=3, column=0, columnspan=5, sticky='nsew')

# Create a label widget inside the frame to create the box outline
linebox_label = tk.Label(linebox_frame, text='', relief='solid', borderwidth=1,
                         height=2)  # Adjust the height value as needed
linebox_label.pack(side="top", fill="both", expand=True)

# Create a label inside the box_frame and center-align it
linefile_name_label = tk.Label(linebox_label, text='')
linefile_name_label.grid(row=0, column=0, sticky='nsew')  # Center-align using grid

# Create a frame to hold the box outline
savelinebox_frame = tk.Frame(files_frame)
savelinebox_frame.grid(row=5, column=0, columnspan=5, sticky='nsew', pady=(0, 10))

# Create a label widget inside the frame to create the box outline
linesavebox_label = tk.Label(savelinebox_frame, text='', relief='solid', borderwidth=1,
                             height=2)  # Adjust the height value as needed
linesavebox_label.pack(side="top", fill="both", expand=True)

# Create a label inside the box_frame and center-align it
savelinefile_name_label = tk.Label(linesavebox_label, text='')
savelinefile_name_label.grid(row=0, column=0, sticky='nsew')  # Center-align using grid

# Create a label widget inside the frame to create the box outline
box_label = tk.Label(box_frame, text='', relief='solid', borderwidth=1, height=2)  # Adjust the height value as needed
box_label.pack(fill=tk.BOTH, expand=True)

# Create a label inside the box_frame and center-align it
file_name_label = tk.Label(box_label, text=str(file_name))
file_name_label.grid(row=0, column=0, sticky='nsew')  # Center-align using grid

file_button = tk.Button(files_frame, text='Open File', command=selectfile)
file_button.grid(row=1, column=5)

linefile_button = tk.Button(files_frame, text='Open File', command=selectlinefile)
linefile_button.grid(row=3, column=5)

linesave_button = tk.Button(files_frame, text='Define File', command=savelinefile)
linesave_button.grid(row=5, column=5, pady=(0, 10))

# Add some space below files_frame
# tk.Label(files_frame, text="").grid(row=4, column=0)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

plotparams_frame = tk.Frame(window, borderwidth=2, relief="groove")
plotparams_frame.grid(row=files_frame.grid_info()['row'] + files_frame.grid_info()['rowspan'], column=0, rowspan=6,
                      columnspan=5, sticky="nsew")

# Create and place the xp1 text box in row 12, column 0
xp1_label = tk.Label(plotparams_frame, text="Plot start:")
xp1_label.grid(row=0, column=0)
xp1_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
xp1_entry.insert(0, str(xp1))
xp1_entry.grid(row=0, column=1)
xp1_entry.bind("<Return>", lambda event: update_xp1_rng())

# Create and place the rng text box in row 12, column 2
rng_label = tk.Label(plotparams_frame, text="Plot range:")
rng_label.grid(row=0, column=2)
rng_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
rng_entry.insert(0, str(rng))
rng_entry.grid(row=0, column=3)
rng_entry.bind("<Return>", lambda event: update_xp1_rng())

# Create and place the min_lamb text box in row 2, column 0
min_lamb_label = tk.Label(plotparams_frame, text="Min. Wave:")
min_lamb_label.grid(row=1, column=0)
min_lamb_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
min_lamb_entry.insert(0, str(min_lamb))
min_lamb_entry.grid(row=1, column=1)
min_lamb_entry.bind("<Return>", lambda event: update_initvals())

# Create and place the max_lamb text box in row 2, column 2
max_lamb_label = tk.Label(plotparams_frame, text="Max. Wave:")
max_lamb_label.grid(row=1, column=2)
max_lamb_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
max_lamb_entry.insert(0, str(max_lamb))
max_lamb_entry.grid(row=1, column=3)
max_lamb_entry.bind("<Return>", lambda event: update_initvals())

# Create and place the dist text box in row 3, column 0
dist_label = tk.Label(plotparams_frame, text="Distance:")
dist_label.grid(row=2, column=0)
dist_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
dist_entry.insert(0, str(dist))
dist_entry.grid(row=2, column=1)
dist_entry.bind("<Return>", lambda event: update_initvals())

# Create and place the RV text box in row 3, column 0
dist_label = tk.Label(plotparams_frame, text="Stellar RV:")
dist_label.grid(row=2, column=2)
star_rv_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
star_rv_entry.insert(0, str(star_rv))
star_rv_entry.grid(row=2, column=3)
star_rv_entry.bind("<Return>", lambda event: update_initvals())

# Create and place the fwhm text box in row 3, column 2
fwhm_label = tk.Label(plotparams_frame, text="FWHM:")
fwhm_label.grid(row=3, column=0)
fwhm_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
fwhm_entry.insert(0, str(fwhm))
fwhm_entry.grid(row=3, column=1)
fwhm_entry.bind("<Return>", lambda event: update_initvals())

# Create and place the fwhm text box in row 3, column 2
intrinsic_line_width_label = tk.Label(plotparams_frame, text="Broadening:")
intrinsic_line_width_label.grid(row=3, column=2)
intrinsic_line_width_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
intrinsic_line_width_entry.insert(0, str(intrinsic_line_width))
intrinsic_line_width_entry.grid(row=3, column=3)
intrinsic_line_width_entry.bind("<Return>", lambda event: update_initvals())

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

# Create a dropdown menu in the new window
spanselectlab = tk.Label(plotparams_frame, text="Molecule:")
#spanselectlab.grid (row=4, column=0, pady=(0, 45))
spanselectlab.grid(row=4, column=0)
spanoptionsvar = [m[0] for m in molecules_data]  # + ["SUM"]
spandropdowntext = tk.StringVar()
spandropd = ttk.Combobox(plotparams_frame, textvariable=spandropdowntext, values=spanoptionsvar, width=6)
spandropd.set(spanoptionsvar[0])
#spandropd.grid (row=4, column=1, pady=(0, 45))
spandropd.grid(row=4, column=1)

spandropd.bind("<<ComboboxSelected>>", lambda event: on_span_select((spanoptionsvar[spandropd.current()]).lower()))

spanmol = (spanoptionsvar[spandropd.current()]).lower()

# Create the buttons for line de-blender
fwhmtolerance_label = tk.Label(plotparams_frame, text="FWHM tol.:")
fwhmtolerance_label.grid(row=5, column=0, pady=(0, 2))
fwhmtolerance_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
fwhmtolerance_entry.insert(0, str(fwhmtolerance))
fwhmtolerance_entry.grid(row=5, column=1, pady=(0, 2))
centrtolerance_label = tk.Label(plotparams_frame, text="Centr. tol.:")
centrtolerance_label.grid(row=5, column=2, pady=(0, 2))
centrtolerance_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
centrtolerance_entry.insert(0, str(centrtolerance))
centrtolerance_entry.grid(row=5, column=3, pady=(0, 2))

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

# Create a Tkinter button to import additional hitran molecules
import_button = tk.Button(title_frame, text="HITRAN query", bg='lightgray', activebackground='gray',
                          command=import_molecule)
import_button.grid(row=0, column=0)

defmol_button = tk.Button(title_frame, text='Default Molecules', bg='lightgray', activebackground='gray',
                          command=lambda: load_defaults_from_file(), width=12, height=1)
defmol_button.grid(row=0, column=1)

# Create the 'Add Mol.' button
addmol_button = tk.Button(title_frame, text='Add Molecule', bg='lightgray', activebackground='gray',
                          command=lambda: add_molecule_data(), width=12, height=1)
addmol_button.grid(row=0, column=2)

# Create the 'Save Changes' button
saveparams_button = tk.Button(title_frame, text='Save Parameters', bg='lightgray', activebackground='gray',
                              command=lambda: saveparams_button_clicked(), width=12, height=1)
saveparams_button.grid(row=0, column=3)

# Create the 'Load Save' button
loadparams_button = tk.Button(title_frame, text='Load Parameters', bg='lightgray', activebackground='gray',
                              command=lambda: load_variables_from_file(file_name), width=12, height=1)
loadparams_button.grid(row=0, column=4)

export_button = tk.Button(title_frame, text='Export Models', bg='lightgray', command=export_spectrum, width=12,
                          height=1)
export_button.grid(row=0, column=5)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="peachpuff", relief=SOLID, borderwidth=1,
                      font=("tahoma", "12", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()




# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------


def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)    

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
"""
print_saved_lines() prints, as vertical dashed lines, on the top graph the locations of all lines saved to the current csv connected to the Save() function.
This csv can be changed in the user adjustable variables code block, but the change won't take into effect until the user regenerates the tool.
"""


def print_saved_lines():
    global linelistpath, green_lines, green_scatter, default_line

    try:
        linelistpath
    except NameError:
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'Input line list is not defined!')
        return

    update()
    ax1.callbacks.connect('xlim_changed', on_xlims_change)

    # Initialize default_line to None at the start
    default_line = None

    green_lines = []
    green_scatter = []

    # Load saved lines
    svd_lns = pd.read_csv(linelistpath, sep=',')
    svd_lamb = np.array(svd_lns['lam'])
    if 'xmin' in svd_lns:
        x_min = np.array(svd_lns['xmin'])
        x_max = np.array(svd_lns['xmax'])

    # Plot vertical lines in ax1 for saved lines
    for i in range(len(svd_lamb)):
        ax1.vlines(svd_lamb[i], -2, 10, linestyles='dashed', color='red')
        if 'xmin' in svd_lns:
            ax1.vlines(x_min[i], -2, 10, color='coral', alpha=0.5)
            ax1.vlines(x_max[i], -2, 10, color='coral', alpha=0.5)

    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Saved lines retrieved from file.')
    canvas.draw()

# -----------------------------------------------------------------------------
# Updates plot x-axis limits based on user input, adjusting ranges and UI entries
# accordingly, then redraws the plot to reflect changes.
# -----------------------------------------------------------------------------
def update_xp1_rng():
    global xp1, rng, xp2
    # Get the values from the Tkinter Entry widgets and convert them to floats
    min_lamb = float(min_lamb_entry.get())
    max_lamb = float(max_lamb_entry.get())
    xp1 = float(xp1_entry.get())
    rng = float(rng_entry.get())
    xp2 = xp1 + rng
    if xp1 < min_lamb or xp1 > max_lamb:
        if xp1 < min_lamb:
            min_lamb = xp1
            min_lamb_entry.delete(0, "end")
            min_lamb_entry.insert(0, str(min_lamb))
        if xp1 > max_lamb:
            max_lamb = xp2
            max_lamb_entry.delete(0, "end")
            max_lamb_entry.insert(0, str(max_lamb))
        update_initvals()
    ax1.set_xlim(xmin=xp1, xmax=xp2)
    print("Updated values: xp1 =", xp1, ", rng =", rng)
    update()
    canvas.draw()

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
    """
pop_diagram() is the function for populating the population diagram with the lines of the water model 
in the entire range of the model
"""


def pop_diagram():
    ax3.clear()
    global spanmol
    ax3.set_ylabel(r'ln(4πF/(hν$A_{u}$$g_{u}$))')
    ax3.set_xlabel(r'$E_{u}$ (K)')
    ax3.set_title('Population diagram', fontsize='medium')

    # Getting all the water lines in the range of min_lamb, max_lamb as set by the user in the adjustable variables code block
    int_pars = eval(f"{spanmol}_intensity.get_table")
    int_pars.index = range(len(int_pars.index))

    # Parsing the components of the lines in int_pars
    wl = int_pars['lam']
    intens_mod = int_pars['intens']
    Astein_mod = int_pars['a_stein']
    gu = int_pars['g_up']
    eu = int_pars['e_up']

    # Calculating the y-axis for the population diagram for each line in int_pars
    area = eval(f"np.pi*({spanmol}_radius*au*1e2)**2")  # In cm^2
    Dist = dist * pc
    beam_s = area / Dist ** 2
    F = intens_mod * beam_s
    freq = ccum / wl
    rd_yax = np.log(4 * np.pi * F / (Astein_mod * hh * freq * gu))
    threshold = np.nanmax(F) / 100

    ax3.set_ylim(np.nanmin(rd_yax[F > threshold]), np.nanmax(rd_yax) + 0.5)
    ax3.set_xlim(np.nanmin(eu) - 50, np.nanmax(eu[F > threshold]))

    # Populating the population diagram graph with the lines
    line6 = ax3.scatter(eu, rd_yax, s=0.5, color='#838B8B')
    # plt.show()

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
    """
model_visible() is connected to the "Visible" button in the tool.
This function turn on/off the visibility of the line for the currently selected model
"""


# Function to update visibility when a button is clicked
def model_visible(event):
    # Update visibility based on the button that was clicked
    if globals()[f"{event}_vis"] == True:
        globals()[f"{event}_vis"] = False

        if event == 'h2o':
            ax1.fill_between(lambdas_h2o, fluxes_h2o, 0, facecolor="red", color='red', alpha=0)
        # Add similar blocks for other molecules
    else:
        globals()[f"{event}_vis"] = True
        if event == 'h2o':
            ax1.fill_between(lambdas_h2o, fluxes_h2o, 0, facecolor="red", color='red', alpha=0.2)
    write_user_csv(molecules_data)

    update()  # Call the update function to refresh the plot
    canvas.draw()

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def choose_color(widget):
    # Get the row number from the widget's grid info
    row = widget.grid_info()["row"]

    # Get the molecule name from the entry widget in the same row
    mol_name = molecule_frame.grid_slaves(row=row, column=0)[0].get().lower()

    # Ask user to choose a color
    color = colorchooser.askcolor(title="Choose a color")
    if color[1]:  # Check if a color was selected
        # Set the color of the molecule line
        globals()[f"{mol_name.lower()}_color"] = color[1]
        exec(f"{mol_name.lower()}_line.set_color('{color[1]}')", globals())
        # Get the color button from the grid_slaves list
        color_button = molecule_frame.grid_slaves(row=row, column=6)[0]

        # Set the background color of the color button
        color_button.configure(bg=color[1])
        write_user_csv(molecules_data)
        update()

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
def delete_row(widget):
    global molecules_data, nextrow

    data_field.delete('1.0', "end")

    row = widget.grid_info()["row"]
    mol_name = molecule_frame.grid_slaves(row=row, column=0)[0].get().lower()

    if mol_name == "h2o":
        data_field.delete('1.0', "end")
        data_field.insert('1.0', f'You can not delete {mol_name.upper()}!')
        return

    # Destroy all widgets in the row
    for w in molecule_frame.grid_slaves(row=row):
        if isinstance(w, tk.Entry) or isinstance(w, tk.Button) or isinstance(w, tk.Checkbutton):
            w.unbind('<Enter>')
            w.unbind('<Leave>')
        w.destroy()

    exec(f"{mol_name.lower()}_line.remove()", globals())

    # Remove the molecule from molecules_data
    molecules_data = [molecule for molecule in molecules_data if molecule[0].lower() != mol_name]

    write_user_csv(molecules_data)

    # Move all rows below this row up by one
    for r in range(row + 1, nextrow):
        for col in range(7):  # Adjust the range if you have more columns
            widget_list = molecule_frame.grid_slaves(row=r, column=col)
            for widget in widget_list:
                widget.grid(row=r - 1, column=col)

    nextrow -= 1

    spanoptionsvar = [m[0] for m in molecules_data]
    spandropd['values'] = spanoptionsvar
    if spanoptionsvar:
        spandropd.set(spanoptionsvar[0])
    update()
    canvas.draw()
    data_field.delete('1.0', "end")
    data_field.insert('1.0', f'{mol_name.upper()} deleted!')

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
def load_molecules_list():
    filename = os.path.join(save_folder, f"molecules_list.csv")

    if os.path.exists(filename):
        try:
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)  # Read the header row
                rows = list(reader)  # Read all rows into a list

                for i, row in enumerate(rows):
                    mol_name, mol_filepath, mol_label, temp, rad, n_mol, color, vis, dist, stellarrv, fwhm, ilw = row

                    # Update global variables or GUI fields with the loaded values
                    exec(f"global t_{mol_name.lower()}; t_{mol_name.lower()} = {temp}")
                    exec(f"global {mol_name.lower()}_radius; {mol_name.lower()}_radius = {rad}")
                    exec(f"global n_mol_{mol_name.lower()}; n_mol_{mol_name.lower()} = {n_mol}")
                    exec(f"global {mol_name.lower()}_line_color; {mol_name.lower()}_line_color = '{color}'")
                    exec(f"global {mol_name.lower()}_color; {mol_name.lower()}_color = '{color}'")
                    exec(f"global {mol_name.lower()}_vis; {mol_name.lower()}_vis = {vis}")
                    exec(f"global dist; dist = {dist}")
                    exec(f"global star_rv; star_rv = {stellarrv}")
                    exec(f"global fwhm; fwhm = {fwhm}")
                    exec(f"global intrinsic_line_width; intrinsic_line_width = {ilw}")

                    # Update GUI fields
                    eval(f"{mol_name.lower()}_temp_field").delete(0, "end")
                    eval(f"{mol_name.lower()}_temp_field").insert(0, temp)

                    eval(f"{mol_name.lower()}_rad_field").delete(0, "end")
                    eval(f"{mol_name.lower()}_rad_field").insert(0, rad)

                    eval(f"{mol_name.lower()}_dens_field").delete(0, "end")
                    eval(f"{mol_name.lower()}_dens_field").insert(0, f"{float(n_mol):.{1}e}")

                    dist_entry.delete(0, "end")
                    dist_entry.insert(0, f"{dist}")

                    star_rv_entry.delete(0, "end")
                    star_rv_entry.insert(0, f"{star_rv}")

                    fwhm_entry.delete(0, "end")
                    fwhm_entry.insert(0, f"{fwhm}")

                    intrinsic_line_width_entry.delete(0, "end")
                    intrinsic_line_width_entry.insert(0, f"{intrinsic_line_width}")

                    # Call update_initvals() only on the last iteration
                    if i == len(rows) - 1:
                        update_initvals()

            # Perform other updates or actions after loading
            spanoptionsvar = [m[0] for m in molecules_data]
            spandropd['values'] = spanoptionsvar
            if spanoptionsvar:
                spandropd.set(spanoptionsvar[0])

            print("Variables loaded from CSV file.")

        except Exception as e:
            print("Error loading variables from CSV:", e)

    for row, (mol_name, _, _) in enumerate(molecules_data, start=1):
        # Get the molecule name in lower case
        mol_name_lower = mol_name.lower()

        # Check if the color variable is defined
        if f"{mol_name_lower}_color" in globals():
            linecolor = eval(f"{mol_name_lower}_color")
            exec(f"{mol_name_lower}_line.set_color('{linecolor}')", globals())

            # Get the line object
            line_var = globals().get(f"{mol_name_lower}_line")

            # Check if the line object exists and has a color attribute
            if line_var and hasattr(line_var, 'get_color'):
                # Get the color of the line
                line_color = line_var.get_color()
                globals()[f"{mol_name_lower}_color"] = line_color

                # Get the color button from the grid_slaves list
                color_button = molecule_frame.grid_slaves(row=row, column=6)[0]
                # Set the background color of the color button
                color_button.configure(bg=line_color)

        # Check if the visibility variable is defined and evaluate it
        if eval(f"{mol_name_lower}_vis"):
            exec(f"{mol_name_lower}_vis_checkbutton.select()")

            if eval(f"{mol_name.lower()}_vis"):
                exec(f"{mol_name.lower()}_vis_checkbutton.select()")

    else:
        data_field.delete('1.0', "end")
        data_field.insert('1.0', 'Saved parameters file not found.')

    update()

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
def loadsavedmessage():
    global data_field
    data_field.delete('1.0', "end")
    data_field.insert('1.0', 'Parameter updated')
    fig.canvas.draw_idle()


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
def on_span_select(selected_item):
    global spanmol
    global model_line_select
    global model_indmin
    global model_indmax

    # Suppress the divide by zero warning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        spanmol = selected_item

        pop_diagram()
        update()

        data_field.insert('1.0', 'Molecule selected: ' + spanmol)

        try:
            model_region_x_str = f"lambdas_{spanmol}[model_indmin:model_indmax]"
            model_region_x = eval(model_region_x_str)

            # Dynamically set the variable
            model_region_y_str = f"fluxes_{spanmol}[model_indmin:model_indmax]"
            model_region_y = eval(model_region_y_str)

            # Suppress the divide by zero warning
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)

            model_line_select.set_data(model_region_x, model_region_y)
            plt.draw()
            canvas.draw()
            fig.canvas.flush_events()
        except NameError:
            # print("model_indmin or model_indmax is not defined.")
            pass

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
        
# Create and place the xp1 text box in row 12, column 0
specsep_label = tk.Label(plotparams_frame, text="Line Separ.:")
#specsep_label.grid (row=4, column=2, pady=(0, 45))
specsep_label.grid(row=4, column=2)
specsep_entry = tk.Entry(plotparams_frame, bg='lightgray', width=8)
specsep_entry.insert(0, str(specsep))
#specsep_entry.grid (row=4, column=3, pady=(0, 45))
specsep_entry.grid(row=4, column=3)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

def export_spectrum():
    # Create a new window for exporting the spectrum
    export_window = tk.Toplevel(root)
    export_window.title("Export Spectrum")

    # Create a label in the new window
    label = tk.Label(export_window, text="Select a molecule:")
    label.grid(row=0, column=0)

    # Create a dropdown menu in the new window
    options = [molecule[0] for molecule in molecules_data] + ["SUM"] + ["ALL"]
    dropdown_var = tk.StringVar()
    dropdown = ttk.Combobox(export_window, textvariable=dropdown_var, values=options)
    dropdown.set(options[0])
    dropdown.grid(row=1, column=0)

    # Create a button in the new window
    button = tk.Button(export_window, text="Generate CSV", command=lambda: generate_csv(dropdown_var.get()))
    button.grid(row=1, column=1)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
def toggle_fullscreen():
    state = window.attributes('-fullscreen')
    window.attributes('-fullscreen', not state)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
def toggle_legend():
    if ax1.legend_ is None:
        ax1.legend()
    else:
        ax1.legend_.remove()
    canvas.draw()

# Create a Tkinter button to toggle the legend
toggle_button = tk.Button(title_frame, text="Toggle Legend", bg='lightgray', activebackground='gray',
                          command=toggle_legend, width=12)
toggle_button.grid(row=0, column=6)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
# Create and place the buttons for other functions
functions_frame = tk.Frame(window, borderwidth=2, relief="groove")
functions_frame.grid(row=plotparams_frame.grid_info()['row'] + plotparams_frame.grid_info()['rowspan'], column=0,
                     rowspan=6, columnspan=5, sticky='nsew')

save_button = tk.Button(functions_frame, text="Save Line", bg='lightgray', activebackground='gray', command=Save,
                        width=13, height=1)
save_button.grid(row=0, column=0)

fit_button = tk.Button(functions_frame, text="Fit Line", bg='lightgray', activebackground='gray', command=fit_onselect,
                       width=13, height=1)
fit_button.grid(row=0, column=1)

savedline_button = tk.Button(functions_frame, text="Show Saved Lines", bg='lightgray', activebackground='gray',
                             command=print_saved_lines, width=13, height=1)
savedline_button.grid(row=1, column=0)

fitsavedline_button = tk.Button(functions_frame, text="Fit Saved Lines", bg='lightgray', activebackground='gray',
                                command=fit_saved_lines, width=13, height=1)
fitsavedline_button.grid(row=1, column=1)

autofind_button = tk.Button(functions_frame, text="Find Single Lines", bg='lightgray', activebackground='gray',
                            command=single_finder, width=13, height=1)
autofind_button.grid(row=2, column=0)

# Create the 'Atomic lines' button
atomlines_button = tk.Button(functions_frame, text='Show Atomic Lines', bg='lightgray', activebackground='gray',
                             command=lambda: print_atomic_lines(), width=13, height=1)
atomlines_button.grid(row=2, column=1)

# Create the 'Slabfit' button
slabfit_button = tk.Button(functions_frame, text='Single Slab Fit', bg='lightgray', activebackground='gray',
                           command=lambda: run_slabfit(), width=13, height=1)
slabfit_button.grid(row=3, column=0)

# Create the 'De-blender' button
deblender_button = tk.Button(functions_frame, text='Line De-blender', bg='lightgray', activebackground='gray',
                             command=lambda: fitmulti_onselect(), width=13, height=1)
deblender_button.grid(row=3, column=1)


# Dictionary to store the references to text boxes for each molecule
molecule_text_boxes = {}

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
# Create a frame for the Text widget
text_frame = tk.Frame(window)
text_frame.grid(row=functions_frame.grid_info()['row'] + functions_frame.grid_info()['rowspan'], column=0,
                columnspan=5, sticky='nsew')

# Create a Text widget within the frame
data_field = tk.Text(text_frame, wrap="word", height=13, width=24)
data_field.pack(fill="both", expand=True)



ax1.callbacks.connect('xlim_changed', on_xlims_change)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

# Create a FigureCanvasTkAgg widget to embed the figure in the tkinter window
canvas = FigureCanvasTkAgg(fig, master=window)
canvas_widget = canvas.get_tk_widget()

# Place the canvas widget in column 9, row 1
canvas_widget.grid(row=1, column=5, rowspan=100, sticky='nsew')

# Allow column 9 and row 1 to expandc
window.grid_columnconfigure(5, weight=1)
window.grid_rowconfigure(100, weight=1)

# Create a frame for the toolbar inside the title_frame
toolbar_frame = tk.Frame(title_frame)
toolbar_frame.grid(row=0, column=9, columnspan=2, sticky="nsew")  # Place the frame in row 0, column 9
# Create a toolbar and update it
toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
toolbar.update()

title_frame.grid_columnconfigure(9, weight=1)

plt.interactive(False)

update()

file_button = tk.Button(files_frame, text='Open File', command=selectfile)
file_button.grid(row=1, column=5)

linefile_button = tk.Button(files_frame, text='Open File', command=selectlinefile)
linefile_button.grid(row=3, column=5)

linesave_button = tk.Button(files_frame, text='Define File', command=savelinefile)
linesave_button.grid(row=5, column=5, pady=(0, 10))


# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

CreateToolTip(import_button, text='Query HITRAN.org\n'
                                  'database to download\n'
                                  'new molecules')

CreateToolTip(addmol_button, text='Add molecule to\n'
                                  'the GUI from files\n'
                                  'downloaded from HITRAN')

CreateToolTip(saveparams_button, text='Save current molecules\n'
                                      'and their parameters\n'
                                      'for this input datafile')

CreateToolTip(loadparams_button, text='Load previously saved\n'
                                      'molecules and parameters\n'
                                      'for this input datafile')

CreateToolTip(defmol_button, text='Load default\n'
                                  'molecule list\n'
                                  'into the GUI')

CreateToolTip(export_button, text='Export current\n'
                                  'models into csv files')

CreateToolTip(toggle_button, text='Turn legend on/off')

CreateToolTip(file_button, text='Select input spectrum datafile')

CreateToolTip(linefile_button, text='Select input line list\n'
                                    'from those available in iSLAT\n'
                                    'or previously saved by the user')

CreateToolTip(linesave_button, text='Select output file\n'
                                    'to save line measurements\n'
                                    'with "Save Line" or "Fit Saved Lines"')

# ---------------------------------------------------------
CreateToolTip(xp1_entry, text='Start wavelength\n'
                              'for the upper plot\n'
                              'units: μm')

CreateToolTip(rng_entry, text='Wavelength range\n'
                              'for the upper plot\n'
                              'units: μm')

CreateToolTip(min_lamb_entry, text='Minimum wavelength\n'
                                   'to calculate the models\n'
                                   'units: μm')

CreateToolTip(max_lamb_entry, text='Maximum wavelength\n'
                                   'to calculate the models\n'
                                   'units: μm')

CreateToolTip(dist_entry, text='Distance to the\n'
                               'observed target\n'
                               'units: pc')

CreateToolTip(star_rv_entry, text='Radial velocity (helioc.)\n'
                                  'of the observed target\n'
                                  'units: km/s')

CreateToolTip(fwhm_entry, text='FWHM for convolution\n'
                               'of the model spectra\n'
                               'units: km/s')

CreateToolTip(intrinsic_line_width_entry, text='Line broadening (FWHM)\n'
                                               '(thermal/turbulence)\n'
                                               'units: km/s')

CreateToolTip(specsep_entry, text='Separation threshold\n'
                                  'for "Find Single Lines"\n'
                                  'units: μm')

CreateToolTip(spandropd, text='Select molecule for line inspection,\n'
                              'the population diagram, and all the\n'
                              'molecule-specific functions')

CreateToolTip(fwhmtolerance_entry, text='Line broadening tolerance\n'
                                        'in de-blender\n'
                                        'units: km/s')

CreateToolTip(centrtolerance_entry, text='Line centroid tolerance\n'
                                         'in de-blender\n'
                                         'units: μm')

# ------------------------------------------------------------------------
CreateToolTip(save_button, text='Save strongest line\n'
                                'from the current line inspection\n'
                                'into the "Output Line Measurements"')

CreateToolTip(fit_button, text='Fit line currently\n'
                               'selected for line inspection')

CreateToolTip(slabfit_button, text='Fit single slab model for molecule\n'
                                   'selected in the drop-down menu\n'
                                   'using flux measurements from input')

CreateToolTip(deblender_button, text='De-blend selected feature\n'
                                     'using a multi-gaussian fit\n'
                                     'with tolerance values above')

CreateToolTip(savedline_button, text='Show saved lines\n'
                                     'from the "Input Line List"')

CreateToolTip(fitsavedline_button, text='Fit all lines from the "Input Line List"\n'
                                        'and save into the "Output Line Measurements"')

CreateToolTip(autofind_button, text='Find single lines\n'
                                    'using separation threshold\n'
                                    'set in the "Line Separ."')

CreateToolTip(atomlines_button, text='Show atomic lines\n'
                                     'from the available line list')

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

for row, (mol_name, _, _) in enumerate(molecules_data, start=1):
    # Get the molecule name in lower case
    mol_name_lower = mol_name.lower()

    # Get the line object
    line_var = globals().get(f"{mol_name_lower}_line")
    # Chdeseck if the line object exists and has a color attribute
    if line_var and hasattr(line_var, 'get_color'):
        # Get the color of the line
        line_color = line_var.get_color()

        # Get the color button from the grid_slaves listatomi
        color_button = molecule_frame.grid_slaves(row=row, column=6)[0]

        # Set the background color of the color button
        color_button.configure(bg=line_color)
    else:
        print('Line object or color attribute not found for:', mol_name)

# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------

load_molecules_list()
window.mainloop()


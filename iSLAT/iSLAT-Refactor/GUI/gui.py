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



# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
    
# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
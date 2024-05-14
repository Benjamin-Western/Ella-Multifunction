print("App is launching, this may take a few seconds, please wait...")


import tkinter as tk
from tkinter import filedialog, Toplevel, Label, Entry, Button
from tkinter import filedialog
from tkinter import *
import zipfile
import os
from datetime import date, datetime
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
import sys
import traceback
from tkinter import ttk, PhotoImage
import logging
import sys
from pathlib import Path
from tkinter import PhotoImage
import requests
from tkinter import messagebox


def send_usage_data(function_name):
    if '--dev' in sys.argv or os.getenv('PYCHARM_HOSTED') == '1':
        print("\nHi Benji")
        return

    try:
        url = f'https://pacific-bastion-05504-99144930b98b.herokuapp.com/track_{function_name}'
        headers = {'Authorization': 'Bearer Benjis_Secret_Key'}
        requests.post(url, headers=headers)
        print('Hello World!')
    except requests.exceptions.RequestException as e:
        print(e)

# Get the path to the user's home directory
home_dir = Path.home()

# Define the path for the log file in the user's home directory
log_file_path = os.path.join(home_dir, 'application_error.log')

# Configure logging to use the user's home directory
logging.basicConfig(filename=log_file_path, level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')


# Ensure matplotlib uses the TkAgg backend to be compatible with Tkinter
plt.switch_backend('TkAgg')

 
# Check if we're running as a PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running in a bundle, set the base path to the temporary directory
    base_path = Path(sys._MEIPASS) / "images"
else:
    # Running in a normal Python environment, set the base path to the images directory
    base_path = Path(__file__).parent / "images"



class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        # Check for consent given in the past
        if not self.check_consent_given():
            # Show the consent notice before initializing the rest of the application
            if not self.show_consent_notice():
                print("Consent not given. Exiting application.")
                self.destroy()  # Destroy all widgets and exit the Tkinter application
                sys.exit()  # Exit the Python script
                return  # Prevent further initialization
            else:
                # User gave consent; store this information for future runs
                self.store_consent_given()
        self.initialize_ui()

    def initialize_ui(self):
        """Initialize the UI components of the application."""
        self.title("Benji's Ella Multifunction App")
        self.geometry("1200x600")

        # Configure the style
        style = ttk.Style(self)
        style.configure('TButton', font=('Arial', 32), padding=(50, 60), borderwidth='20')
        style.map('TButton', foreground=[('active', 'black')], background=[('active', 'white')])

        # Create buttons using the styled TButton
        ttk.Button(self, text="Extract Cydat Files", style='TButton', command=self.open_extract_cydat_window).pack(pady=4, padx=10, expand=False)
        ttk.Button(self, text="Plot all QCs (levey-jennings control chart)", style='TButton', command=self.open_run_qc_window).pack(pady=4, padx=10, expand=False)
        ttk.Button(self, text="Plot all Replicates", style='TButton', command=self.open_handle_duplicates_window).pack(pady=4, padx=10, expand=False)

        # Bind this function to the main window's focus event
        self.bind("<FocusIn>", lambda event: self.reapply_button_styles())


    def check_consent_given(self):
        """Check if the user has already given consent in the past."""
        consent_file_path = os.path.join(os.path.expanduser('~'), '.your_app_consent')
        if os.path.exists(consent_file_path):
            # Get file creation time and convert it to a readable format
            creation_time = os.path.getctime(consent_file_path)
            readable_time = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d')  # Adjusted usage here
            print(
                f"Consent already given on {readable_time}. If you want to withdraw your consent, delete this file: {consent_file_path}")
            return True
        else:
            return False


    def store_consent_given(self):
        """Store the user's consent decision for future runs."""
        consent_file_path = os.path.join(os.path.expanduser('~'), '.your_app_consent')
        with open(consent_file_path, 'w') as consent_file:
            consent_file.write(
            "This tool was developed by Dr. Benjamin Djian (Team Leader ASD FAS EMEA)\nwith the assistance of ChatGPT "
            "(for coding skills)\nand Dr. Christina Wolf (Scientific Support Specialist EMEA Technical Services) for "
            "valuable suggestions regarding user needs.\n\n"
            "This tool is designed for internal use only.\nIf you decide to share it with customers, "
            "please be aware that you do so under your own responsibility.\n\n"
            "It monitors the usage frequency of its main functions to improve understanding of user engagement\n"
            "and preferences, without collecting any personal or input data from users.\n\n"
            "By clicking 'OK', you agree to the terms outlined above."
        )

    def show_consent_notice(self):
        """
        Show a consent notice dialog including developer credits, the internal nature of the tool, sharing responsibilities,
        and data usage consent; return True if consent is given, False otherwise.
        """
        consent_message = (
            "This tool was developed by Dr. Benjamin Djian (Team Leader ASD FAS EMEA) with the assistance of ChatGPT "
            "(for coding skills) and Dr. Christina Wolf (Scientific Support Specialist EMEA Technical Services) for "
            "valuable suggestions regarding user needs.\n\n"
            "This tool is designed for internal use only. If you decide to share it with customers, "
            "please be aware that you do so under your own responsibility.\n\n"
            "It monitors the usage frequency of its main functions to improve understanding of user engagement "
            "and preferences, without collecting any personal or input data from users.\n\n"
            "By clicking 'OK', you agree to the terms outlined above."
        )

        consent_given = messagebox.askokcancel("Consent", consent_message)
        return consent_given

    def close_application(self):
        self.quit()

    def open_extract_cydat_window(self):
        new_window = Toplevel(self)
        ExtractCydatWindow(new_window, self)

    def open_run_qc_window(self):
        new_window = Toplevel(self)
        RunQCWindow(new_window, self)

    def open_handle_duplicates_window(self):
        new_window = Toplevel(self)
        HandleDuplicatesWindow(new_window, self)

    def reapply_button_styles(self):
        style = ttk.Style(self)
        style.configure('TButton', font=('Arial', 32), padding=(50, 60), borderwidth='20')
        style.map('TButton', foreground=[('active', 'black')], background=[('active', 'white')])




class PopupWaitWindow:
    def __init__(self, parent):
        self.top = Toplevel(parent)
        self.top.title("Processing...")
        # Set window size and position
        self.top.geometry("400x100+{0}+{1}".format(parent.winfo_x()+100, parent.winfo_y()+50))
        self.top.transient(parent)  # Set to be on top of the main application window
        # Make window modal
        self.top.grab_set()
        # Message
        msg = Label(self.top, text="This may take up to 1 minute, please wait...")
        msg.pack(side="top", fill="x", pady=20)
        # Prevent resizing
        self.top.resizable(False, False)
        # This will remove the minimize/maximize buttons
        self.top.attributes("-toolwindow", True)

class CustomImageButton(tk.Label):
    def __init__(self, master=None, image=None, hover_image=None, click_image=None, command=None, **kw):
        super().__init__(master, image=image, **kw)
        self.image_normal = image
        self.image_hover = hover_image if hover_image else image
        self.image_click = click_image
        self.command = command

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_enter(self, event):
        if self.image_hover:
            self.config(image=self.image_hover)

    def on_leave(self, event):
        self.config(image=self.image_normal)

    def on_click(self, event):
        if self.image_click:
            self.config(image=self.image_click)

    def on_release(self, event):
        self.config(image=self.image_normal)
        if self.command:
            self.command()

class ExtractCydatWindow:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app  # Reference to the main application
        self.root.title("Extract Cydat Files")
        self.root.geometry("1000x300")  # Adjusted to fit the button

        # Configure unique style for ttk widgets in this window
        self.configure_styles()

        # Input Path Label
        self.input_path_label = ttk.Label(self.root, text="Input Path:", style='ExtractCydat.TLabel')
        self.input_path_label.pack()

        # Input Path Entry
        self.input_path_entry = ttk.Entry(self.root, width=130, style='ExtractCydat.TEntry')
        self.input_path_entry.pack()


        # Select File Button
        self.select_file_button = ttk.Button(self.root, text="Select a folder containing the 'SimplePlexDiagnosticData' zip file(s)",
                                             command=self.select_file, style='select.TButton')
        self.select_file_button.pack()


        # Load images for the button states
        extractcydats_default = PhotoImage(file=str(base_path / "extractcydats_default.png"))
        letsgo = PhotoImage(file=str(base_path / "Letsgo.png"))
        extractcydats_hover = PhotoImage(file=str(base_path / "extractcydats_hover.png"))

        # Extract Cydats Button
        self.run_extract_cydat_button = CustomImageButton(self.root, image=extractcydats_default, hover_image=extractcydats_hover, click_image=letsgo, command=self.extract_cydat)
        self.run_extract_cydat_button.pack(pady=10)



    def configure_styles(self):
        """Configures unique styles for the ExtractCydatWindow."""
        style = ttk.Style()
        style.configure('ExtractCydat.TLabel', font=('Arial', 10))
        style.configure('ExtractCydat.TEntry', font=('Arial', 10), padding=5)
        style.configure('select.TButton', font=('Arial', 12), padding=5)
        # The CustomImageButton does not use ttk.Style, so no changes needed there

    def select_file(self):
        """Opens a dialog for selecting a directory and updates the input path entry with the selected directory."""
        input_path = filedialog.askdirectory()
        self.input_path_entry.delete(0, tk.END)
        self.input_path_entry.insert(0, input_path)

        # Bring the window back to the forefront and direct all input to it
        self.root.lift()
        self.root.grab_set()


    def extract_cydat(self):
        try:
            # Show the popup
            popup = PopupWaitWindow(self.root)
            self.root.update()  # Force the update of the UI to display the popup

            extraction_folder = "cydat_files"
            input_path = self.input_path_entry.get()
            os.chdir(input_path)

            if not os.path.exists(extraction_folder):
                os.makedirs(extraction_folder)

            for input_path, subdirs, files in os.walk(input_path):
                for filename in files:
                    f = os.path.join(input_path, filename)
                    if f.endswith('.zip'):
                        zf = zipfile.ZipFile(f, 'r')
                        cydat_files = []
                        for name in zf.namelist():
                            if name.endswith('.cydat') and not name.endswith('Incomplete.cydat'):
                                cydat_files.append(name)

                        for name in cydat_files:
                            output_path = os.path.join(extraction_folder, os.path.basename(name))
                            with zf.open(name) as src, open(output_path, "wb") as dst:
                                dst.write(src.read())

        except Exception as e:
            # Log the exception
            logging.error("An error occurred during extraction: ", exc_info=True)

        finally:
            send_usage_data('function1')  # Track usage of function1
            popup.top.destroy()
            self.root.update()  # Optional, forces the UI to update after closing the popup
            self.main_app.close_application()

class RunQCWindow:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app  # Reference to the main application
        self.root.title("Plot all QCs (levey-jennings control chart) and calculate %CV")
        self.root.geometry("1100x500")  # Adjusted to fit the button

        # Date and time setup
        today = date.today()
        now = datetime.now()
        self.day = today.strftime("%d-%b-%Y")
        self.time = now.strftime("%H_%M_%S")

        # UI Components
        self.create_widgets()


    def create_widgets(self):
        OPTIONS = ['LotNumber', 'AnalyzerName', 'KitId']

        # Configure global styles
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 10), padding=5)
        style.configure('TEntry', padding=5)
        style.configure('select.TButton', font=('Arial', 10), padding=5)
        style.configure('run.TButton', font=('Arial', 42), padding=5)
        style.configure('TRadiobutton', font=('Arial', 10), padding=5)

        # Input and Output File Selection
        input_path_label = ttk.Label(self.root, text="Input File (select your KitsExport in .csv format):", style='TLabel')
        input_path_label.grid(row=0, column=0, padx=10, pady=10)
        self.input_path_entry = ttk.Entry(self.root, width=90, style='TEntry')
        self.input_path_entry.grid(row=0, column=1, padx=10, pady=10)
        input_file_button = ttk.Button(self.root, text="Select", command=self.input_file_select, style='select.TButton')
        input_file_button.grid(row=0, column=2, padx=10, pady=10)

        output_path_label = ttk.Label(self.root, text="Output Path (select the folder where the graphs should be saved):", style='TLabel')
        output_path_label.grid(row=1, column=0, padx=10, pady=1)
        self.output_path_entry = ttk.Entry(self.root, width=90, style='TEntry')
        self.output_path_entry.grid(row=1, column=1, padx=10, pady=1)
        output_path_button = ttk.Button(self.root, text="Select", command=self.output_path_select, style='select.TButton')
        output_path_button.grid(row=1, column=2, padx=10, pady=1)

        # QC Sample Names
        high_qc_label = ttk.Label(self.root, text='High QC Sample (enter exact name):', style='TLabel')
        high_qc_label.grid(row=2, column=0)
        self.high_qc_entry = ttk.Entry(self.root, width=40, style='TEntry')
        self.high_qc_entry.grid(row=2, column=1, sticky='W', pady=10)

        low_qc_label = ttk.Label(self.root, text='Low QC Sample (enter exact name):', style='TLabel')
        low_qc_label.grid(row=3, column=0)
        self.low_qc_entry = ttk.Entry(self.root, width=40, style='TEntry')
        self.low_qc_entry.grid(row=3, column=1, sticky='W', pady=1)

        # Label for Radio Buttons Explanation
        Benji_blank_label = ttk.Label(self.root, text=" ", style='TLabel')
        Benji_blank_label.grid(row=4, column=0, columnspan=3, sticky='W')

        # Label for Radio Buttons Explanation
        radio_button_explanation_label = ttk.Label(self.root,
                                                   text="Select the variable according to which markers on the graphs will be colored:",
                                                   style='TLabel')
        radio_button_explanation_label.grid(row=5, column=0, columnspan=3, sticky='W')

        # Radio Buttons for Options
        self.Selected_tick = tk.StringVar()
        self.Selected_tick.set(OPTIONS[0])

        for i, option in enumerate(OPTIONS):
            ttk.Radiobutton(self.root, text=option, variable=self.Selected_tick, value=option,
                            command=lambda: print(self.Selected_tick.get()), style='TRadiobutton').grid(row=i + 6,
                                                                                                        column=0,
                                                                                                        columnspan=3)

        # Load images for the button states
        graph_qc_default = PhotoImage(file=str(base_path / "Graph_QC_default.png"))
        letsgo = PhotoImage(file=str(base_path / "Letsgo.png"))
        graph_qc_hover = PhotoImage(file=str(base_path / "Graph_QC_Hover.png"))

        # Run QC Button
        run_QC_button = CustomImageButton(self.root, image=graph_qc_default, hover_image=graph_qc_hover,
                                          click_image=letsgo, command=self.run_QC_program)
        run_QC_button.grid(row=9, column=0, columnspan=3, padx=30, pady=20)

    def input_file_select(self):
        # Implementation of input file selection
        input_path = filedialog.askopenfilename(title="Select a CSV file", filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        self.input_path_entry.delete(0, tk.END)
        self.input_path_entry.insert(0, input_path)
        self.root.lift()
        self.root.grab_set()

    def output_path_select(self):
        # Implementation of output path selection
        output_path = filedialog.askdirectory()
        self.output_path_entry.delete(0, tk.END)
        self.output_path_entry.insert(0, output_path)
        self.root.lift()
        self.root.grab_set()

    def change_dates(self, df):
        """Converts 'RunDate' in DataFrame to a new format and stores it in 'New_Date'."""
        new_dates = []
        for i in df['RunDate']:
            rundate = re.split(':| ', i)
            datetimeobject = datetime.strptime(rundate[0], '%m/%d/%Y')
            newformat = datetimeobject.strftime('%Y_%m_%d')
            finaltime = newformat + '_' + rundate[1] + '_' + rundate[2]
            new_dates.append(finaltime)
        df['New_Date'] = new_dates
        return df

    def make_lists(self, df, selected_tick):
        GRAPH_BY = 'AnalyteName'
        SERIAL_NUMBER = 'AnalyzerName'
        Y_DATA = 'CalculatedConcentration'
        X_DATA = 'New_Date'
        SAMPLE_NAME = "SampleName"
        Color_by = selected_tick
        list_of_columns = [SAMPLE_NAME, GRAPH_BY, selected_tick, X_DATA, Y_DATA]
        list_of_Lots_or_Analyzer = list(set(df[selected_tick]))
        list_of_analytes = list(set(df[GRAPH_BY]))
        list_of_sample = list(set(df['SampleName']))
        list_of_kits = list(set(df['KitId']))
        list_of_Ellas = [str(i) for i in set(df[SERIAL_NUMBER])]
        all_used_ellas = '_'.join(list_of_Ellas)
        print(list_of_Ellas)
        return list_of_columns, list_of_Lots_or_Analyzer, list_of_analytes, list_of_sample, list_of_kits, all_used_ellas, Color_by




    def generate_QC_graphs(self, df, list_of_QC, list_of_columns, list_of_analytes, list_of_Lots_or_Analyzer, Color_by):
        # Defining constants and column names
        GRAPH_BY = 'AnalyteName'
        Y_DATA = 'CalculatedConcentration'
        X_DATA = 'New_Date'
        InletNumber = 'InletNumber'
        KitId = 'KitId'
        LABEL_COLOR = [
            "#9370DB", "#C71585", "#20B2AA", "#00BFFF", "#D2B48C", "#32CD32", "#808080",
            "#DAA520", "#9ACD32", "#E6E6FA", "#FFC0CB", "#7FFFD4", "#ADD8E6", "#F5F5DC", "#90EE90",
            "#C0C0C0", "#F5DEB3", "#7FFF00", "#00FFFF", "#808000", "#008080", "#EE82EE", "#0000FF", "#FA8072",
            "#FF6347",
            "#FF0000", "#800000", "#FFFF00", "#808000", "#00FF00", "#008000", "#00FFFF", "#008080",
            "#0000FF", "#000080", "#FF00FF", "#800080", "#FF4500", "#DA70D6", "#EEE8AA", "#98FB98",
            "#AFEEEE", "#DB7093", "#FFEFD5", "#FFDAB9", "#CD853F", "#FFC0CB", "#DDA0DD", "#B0E0E6", "#800080"
        ]
        list_of_columns.extend([InletNumber, KitId])
        df_QC = df[df["SampleName"].isin(list_of_QC)][list_of_columns]
        df_QC.dropna(subset=["CalculatedConcentration"], inplace=True)
        df_QC.sort_values('New_Date', inplace=True)

        for y in list_of_analytes:
            df_target = df_QC[df_QC[GRAPH_BY] == y]
            df_target = df_target.groupby(['SampleName'], sort=True, as_index=False).agg(
                {'CalculatedConcentration': ['mean', 'std', 'count']})
            df_target['CV'] = (100 * df_target["CalculatedConcentration"]["std"] / df_target["CalculatedConcentration"][
                "mean"]).round(2).astype(str) + "%"
            for index_2, QC in enumerate(list_of_QC):
                try:
                    List_of_Concentrations = []
                    fig, ax = plt.subplots(figsize=(15, 8))
                    Average = np.mean((df_QC.loc[(df_QC[GRAPH_BY] == y) & (df_QC["SampleName"] == QC), Y_DATA]))
                    Stdev = np.std((df_QC.loc[(df_QC[GRAPH_BY] == y) & (df_QC["SampleName"] == QC), Y_DATA]))
                    List_of_Concentrations = df_QC.loc[
                        (df_QC[GRAPH_BY] == y) & (df_QC["SampleName"] == QC), Y_DATA].tolist()
                    # ax.set_yscale('log')
                    ax.set_title(str(QC) + " - " + str(y), fontsize=16)
                    ax.set_ylabel('Concentration (pg/mL)', fontsize=20)
                    if len(X_DATA) < 16:
                        X_FontSize = 16
                    elif len(X_DATA) > 16 and len(X_DATA) < 32:
                        X_FontSize = 12
                    else:
                        X_FontSize = 8
                    ax.tick_params(axis="x", labelsize=X_FontSize, rotation=90)
                    ax.tick_params(axis="y", labelsize=20)
                    for index_3, z in enumerate(list_of_Lots_or_Analyzer):
                        if index_3 == 0:
                            lot_or_Analyzer_in_df = list(set(df[Color_by].tolist()))
                            print(lot_or_Analyzer_in_df)
                        if z in lot_or_Analyzer_in_df:
                            plt.scatter(
                                df_QC.loc[
                                    (df_QC[GRAPH_BY] == y) & (df[Color_by] == z) & (df_QC["SampleName"] == QC), X_DATA],
                                df_QC.loc[
                                    (df_QC[GRAPH_BY] == y) & (df[Color_by] == z) & (df_QC["SampleName"] == QC), Y_DATA],
                                marker="x", s=80, color=LABEL_COLOR[index_3 % len(LABEL_COLOR)],
                                label=str(Color_by) + ': ' + str(z))
                    xlim = ax.get_xlim()
                    plt.hlines(Average, xlim[0], xlim[1], linestyles='dashed', color='r', linewidth=1)
                    plt.hlines((Average + 1 * Stdev), xlim[0], xlim[1], linestyles='dashed', linewidth=1)
                    plt.hlines((Average - 1 * Stdev), xlim[0], xlim[1], linestyles='dashed', linewidth=1)
                    plt.hlines((Average + 2 * Stdev), xlim[0], xlim[1], linestyles='dashed', linewidth=1)
                    plt.hlines((Average - 2 * Stdev), xlim[0], xlim[1], linestyles='dashed', linewidth=1)
                    plt.hlines((Average + 3 * Stdev), xlim[0], xlim[1], linestyles='dashed', linewidth=1)
                    plt.hlines((Average - 3 * Stdev), xlim[0], xlim[1], linestyles='dashed', linewidth=1)
                    ylim = ax.get_ylim()
                    print(y)
                    print(QC)
                    print(df_target.loc[df_target["SampleName"] == QC, "CV"].item())
                    ax.text(xlim[0], (ylim[1] * 1.01),
                            'CV = ' + str(df_target.loc[df_target["SampleName"] == QC, "CV"].item()), fontsize=16)
                    ax.text(xlim[1] * 0.95, (ylim[1] * 1.01), 'n = ' + str(
                        df_target.loc[df_target["SampleName"] == QC, "CalculatedConcentration"]["count"].item()),
                            fontsize=16)
                    df_QC.loc[(df_QC[GRAPH_BY] == y) & (df_QC["SampleName"] == QC)].to_csv(r'_' + str(y) + QC + '.csv',
                                                                                           index=False)
                    ax.legend(loc='upper left', fontsize=10, bbox_to_anchor=(1.01, 1))
                    fig.tight_layout(
                        #rect=[0, 0, 1, 1]
                    )  # Adjust the right boundary of the layout.
                    fig.savefig(str(QC) + " QC _ " + str(y) + '.png')
                except ValueError as e:
                    print(f"A ValueError occurred: {e}", file=sys.stderr)
                    traceback.print_exc()  # This will print the traceback of the exception
                    continue
                except Exception as e:
                    print(f"An unexpected error occurred: {e}", file=sys.stderr)
                    traceback.print_exc()  # This will print the traceback of the exception
                    continue


    def run_QC_program(self):
        try:
            # Show the popup
            popup = PopupWaitWindow(self.root)
            self.root.update()  # Force the update of the UI to display the popup

            today = date.today()
            now = datetime.now()
            day = today.strftime("%d-%b-%Y")
            time = now.strftime("%H_%M_%S")

            input_path = self.input_path_entry.get()
            output_path = self.output_path_entry.get()
            high_qc_name = self.high_qc_entry.get()
            low_qc_name = self.low_qc_entry.get()
            df = pd.read_csv(input_path)
            df = self.change_dates(df)
            list_of_QC = [high_qc_name, low_qc_name]
            selected_tick = self.Selected_tick.get()
            list_of_columns, list_of_Lots_or_Analyzer, list_of_analytes, list_of_sample, list_of_kits, all_used_ellas, Color_by = self.make_lists(
                df, selected_tick)
            path_for_graphs = output_path + '/New_Folder_' + str(all_used_ellas) + '_' + str(today) + '_' + str(time)
            if not os.path.exists(path_for_graphs):
                os.makedirs(path_for_graphs)
            os.chdir(path_for_graphs)
            try:
                self.generate_QC_graphs(df, list_of_QC, list_of_columns, list_of_analytes, list_of_Lots_or_Analyzer,
                                   selected_tick)
            except:
                ValueError

        except Exception as e:
            # Log the exception
            logging.error("An error occurred during extraction: ", exc_info=True)

        finally:
            send_usage_data('function2')  # Track usage of function1
            popup.top.destroy()
            self.root.update()  # Optional, forces the UI to update after closing the popup
            self.main_app.close_application()



class HandleDuplicatesWindow:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app  # Reference to the main application
        self.root.title("Plot all Replicates")
        self.root.geometry("1100x440")  # Adjusted to fit the button

        # Date and time setup
        today = date.today()
        now = datetime.now()
        self.day = today.strftime("%d-%b-%Y")
        self.time = now.strftime("%H_%M_%S")

        # UI Components
        self.create_widgets()


    def create_widgets(self):
        OPTIONS = ['LotNumber', 'AnalyzerName', 'KitId']

        # Configure global styles
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 10), padding=5)
        style.configure('TEntry', padding=5)
        style.configure('select.TButton', font=('Arial', 10), padding=5)
        style.configure('run.TButton', font=('Arial', 42), padding=5)
        style.configure('TRadiobutton', font=('Arial', 10), padding=5)

        # Input and Output File Selection
        input_path_label = ttk.Label(self.root, text="Input File (select your KitsExport in .csv format):", style='TLabel')
        input_path_label.grid(row=0, column=0, padx=10, pady=10)
        self.input_path_entry = ttk.Entry(self.root, width=90, style='TEntry')
        self.input_path_entry.grid(row=0, column=1, padx=10, pady=10)
        input_file_button = ttk.Button(self.root, text="Select", command=self.input_file_select, style='select.TButton')
        input_file_button.grid(row=0, column=2, padx=10, pady=10)

        output_path_label = ttk.Label(self.root, text="Output Path (select the folder where the graphs should be saved):", style='TLabel')
        output_path_label.grid(row=1, column=0, padx=10, pady=1)
        self.output_path_entry = ttk.Entry(self.root, width=90, style='TEntry')
        self.output_path_entry.grid(row=1, column=1, padx=10, pady=1)
        output_path_button = ttk.Button(self.root, text="Select", command=self.output_path_select, style='select.TButton')
        output_path_button.grid(row=1, column=2, padx=10, pady=1)
        Benji_label = ttk.Label(self.root, text=" ", style='TLabel')
        Benji_label.grid(row=3, column=0, columnspan=3, sticky='W', pady=1)

        # Label for Radio Buttons Explanation
        radio_button_explanation_label = ttk.Label(self.root,
                                                   text="Select the variable according to which markers on the graphs will be colored:",
                                                   style='TLabel')
        radio_button_explanation_label.grid(row=4, column=0, columnspan=3, sticky='W', pady=5)

        # Radio Buttons for Options
        self.Selected_tick = tk.StringVar()
        self.Selected_tick.set(OPTIONS[0])

        for i, option in enumerate(OPTIONS):
            ttk.Radiobutton(self.root, text=option, variable=self.Selected_tick, value=option,
                            command=lambda: print(self.Selected_tick.get()), style='TRadiobutton').grid(row=i + 6,
                                                                                                        column=0,
                                                                                                        columnspan=3)

        # Load images for the button states
        graph_replicates_default = PhotoImage(file=str(base_path / "Graph_replicates_default.png"))
        letsgo = PhotoImage(file=str(base_path / "Letsgo.png"))
        graph_replicates_hover = PhotoImage(file=str(base_path / "Graph_replicates_hover.png"))


        # Run duplicates Button
        run_duplicates_button = CustomImageButton(self.root, image=graph_replicates_default, hover_image=graph_replicates_hover,
                                                  click_image=letsgo, command=self.run_duplicate_program)
        run_duplicates_button.grid(row=9, column=0, columnspan=3, padx=30, pady=20)


    def input_file_select(self):
        # Implementation of input file selection
        input_path = filedialog.askopenfilename(title="Select a CSV file", filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        self.input_path_entry.delete(0, tk.END)
        self.input_path_entry.insert(0, input_path)
        self.root.lift()
        self.root.grab_set()

    def output_path_select(self):
        # Implementation of output path selection
        output_path = filedialog.askdirectory()
        self.output_path_entry.delete(0, tk.END)
        self.output_path_entry.insert(0, output_path)
        self.root.lift()
        self.root.grab_set()

    def change_dates(self, df):
        """Converts 'RunDate' in DataFrame to a new format and stores it in 'New_Date'."""
        new_dates = []
        for i in df['RunDate']:
            rundate = re.split(':| ', i)
            datetimeobject = datetime.strptime(rundate[0], '%m/%d/%Y')
            newformat = datetimeobject.strftime('%Y_%m_%d')
            finaltime = newformat + '_' + rundate[1] + '_' + rundate[2]
            new_dates.append(finaltime)
        df['New_Date'] = new_dates
        return df

    def make_lists(self, df, selected_tick):
        GRAPH_BY = 'AnalyteName'
        SERIAL_NUMBER = 'AnalyzerName'
        Y_DATA = 'CalculatedConcentration'
        X_DATA = 'New_Date'
        SAMPLE_NAME = "SampleName"
        Color_by = selected_tick
        list_of_columns = [SAMPLE_NAME, GRAPH_BY, selected_tick, X_DATA, Y_DATA]
        list_of_Lots_or_Analyzer = list(set(df[selected_tick]))
        list_of_analytes = list(set(df[GRAPH_BY]))
        list_of_sample = list(set(df['SampleName']))
        list_of_kits = list(set(df['KitId']))
        list_of_Ellas = [str(i) for i in set(df[SERIAL_NUMBER])]
        all_used_ellas = '_'.join(list_of_Ellas)
        print(list_of_Ellas)
        return list_of_columns, list_of_Lots_or_Analyzer, list_of_analytes, list_of_sample, list_of_kits, all_used_ellas, Color_by


    def filter_for_duplicates(self, df):
        df_clean = df.dropna(subset=['SampleName', 'AnalyteName', 'CalculatedConcentration'])
        counts = df_clean.groupby(['SampleName', 'AnalyteName']).size().reset_index(name='Counts')
        true_replicates = counts[counts['Counts'] > 1]
        df_true_replicates = pd.merge(df, true_replicates[['SampleName', 'AnalyteName']],
                                      on=['SampleName', 'AnalyteName'],
                                      how='inner')
        return df_true_replicates

    def generate_duplicate_graph(self, df, list_of_analytes, list_of_Lots_or_Analyzer, Color_by, LABEL_COLOR):
        SAMPLE_NAME = "SampleName"
        GRAPH_BY = 'AnalyteName'
        Y_DATA = 'CalculatedConcentration'
        InletNumber = 'InletNumber'
        KitId = 'KitId'
        for y in list_of_analytes:
            print(y)
            fig, ax = plt.subplots(figsize=(15, 6))
            ax.set_yscale('log')
            df_target = df[(df[GRAPH_BY] == y)]  # Filter for target analyte
            ax.set_title(y, fontsize=16)
            ax.set_ylabel('Concentration (pg/mL)', fontsize=20)
            ax.tick_params(axis="x", labelsize=12, rotation=90)
            ax.tick_params(axis="y", labelsize=20)

            for index, z in enumerate(list_of_Lots_or_Analyzer):
                if z in df_target[Color_by].unique():
                    df_lot = df_target[df_target[Color_by] == z]
                    plt.scatter(
                        df_lot[SAMPLE_NAME],
                        df_lot[Y_DATA],
                        marker="x", s=80, color=LABEL_COLOR[index % len(LABEL_COLOR)], label=f"{Color_by}: {z}")

            ax.legend(loc='upper left', fontsize=10, bbox_to_anchor=(1.01, 1))
            fig.tight_layout()

            def kit_inlet_pairs(group):
                pairs = group.apply(lambda x: f"{x[KitId]};{x[InletNumber]}", axis=1)
                return '\n'.join(pairs.unique())

            cv_data = df[df[GRAPH_BY] == y].groupby(SAMPLE_NAME).agg(
                CV_Percent=('CalculatedConcentration', lambda x: np.std(x, ddof=1) / np.mean(x) * 100),
                Count=('CalculatedConcentration', 'count'),
                KitId_InletNumber=(SAMPLE_NAME, lambda grp: kit_inlet_pairs(df.loc[grp.index]))
            )
            safe_y = re.sub(r'[^\w\s-]', '', str(y)).strip().replace(' ', '_')
            cv_data.to_csv(f"{safe_y}_CV.csv")
            fig.savefig(f"{safe_y}.png")
            plt.close(fig)



    def run_duplicate_program(self):
        try:
            # Show the popup
            popup = PopupWaitWindow(self.root)
            self.root.update()  # Force the update of the UI to display the popup

            today = date.today()
            now = datetime.now()
            self.day = today.strftime("%d-%b-%Y")
            time = self.time = now.strftime("%H_%M_%S")
            LABEL_COLOR = [
                "#9370DB", "#C71585", "#20B2AA", "#00BFFF", "#D2B48C", "#32CD32", "#808080",
                "#DAA520", "#9ACD32", "#E6E6FA", "#FFC0CB", "#7FFFD4", "#ADD8E6", "#F5F5DC", "#90EE90",
                "#C0C0C0", "#F5DEB3", "#7FFF00", "#00FFFF", "#808000", "#008080", "#EE82EE", "#0000FF", "#FA8072",
                "#FF6347",
                "#FF0000", "#800000", "#FFFF00", "#808000", "#00FF00", "#008000", "#00FFFF", "#008080",
                "#0000FF", "#000080", "#FF00FF", "#800080", "#FF4500", "#DA70D6", "#EEE8AA", "#98FB98",
                "#AFEEEE", "#DB7093", "#FFEFD5", "#FFDAB9", "#CD853F", "#FFC0CB", "#DDA0DD", "#B0E0E6", "#800080"
            ]
            input_path = self.input_path_entry.get()  # Assuming this retrieves a file path from your GUI
            output_path = self.output_path_entry.get()  # Assuming this retrieves a file path from your GUI
            df = pd.read_csv(input_path)
            df = self.change_dates(df)
            selected_tick = self.Selected_tick.get()
            list_of_columns, list_of_Lots_or_Analyzer, list_of_analytes, list_of_sample, list_of_kits, all_used_ellas, Color_by = self.make_lists(
                df, selected_tick)
            path_for_graphs = output_path + '/New_Folder_' + str(all_used_ellas) + '_' + str(today) + '_' + str(time)
            today_formatted = date.today().strftime("%Y-%m-%d")
            now_formatted = datetime.now().strftime("%H_%M_%S")
            path_for_graphs = os.path.join(output_path,
                                           'New_Folder_' + all_used_ellas + '_' + today_formatted + '_' + now_formatted)
            if not os.path.exists(path_for_graphs):
                os.makedirs(path_for_graphs)
            os.chdir(path_for_graphs)
            # analyte_max = df["AnalyteNumber"].max()  # Assuming you have an "AnalyteNumber" column
            df_filter = self.filter_for_duplicates(df)
            self.generate_duplicate_graph(df_filter, list_of_analytes, list_of_Lots_or_Analyzer, Color_by, LABEL_COLOR)
            print("Input path: ", input_path)
            print("Output path: ", path_for_graphs)
        except Exception as e:
            # Log the exception
            logging.error("An error occurred during extraction: ", exc_info=True)

        finally:
            send_usage_data('function3')  # Track usage of function1
            popup.top.destroy()
            self.root.update()  # Optional, forces the UI to update after closing the popup
            self.main_app.close_application()



if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()







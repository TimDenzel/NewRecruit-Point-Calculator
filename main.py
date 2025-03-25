import csv
import json
import os
import sys
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
from collections import OrderedDict
from CTkMenuBar import *

# Dictionaries for keeping the order of units and duplicate names
unit_costs = OrderedDict()
name_counter = OrderedDict()
unit_counter_names = OrderedDict()
unit_counter = OrderedDict()
general = OrderedDict()
general_counter = OrderedDict()
units = OrderedDict()

# Global variables
source_file_path = ""
savefile_path = ""
save_destination_path = ""
root = ctk.CTk()
calculator_frame = ctk.CTkFrame(root)
army_name = ctk.StringVar(value="")
spent_points = ctk.StringVar(value="0")
army_points = ctk.StringVar(value="0")
lost_points_total = ctk.StringVar(value="0")
entry_after_ids = {}

if getattr(sys, 'frozen', False):
    icon_path = os.path.join(sys._MEIPASS, 'newRecruit.ico')
else:
    icon_path = 'newRecruit.ico'


class ArmyDetailDialog:
    def __init__(self):
        self.parent = root
        self.title = "Custom Army Options"
        self.result = None

        self.dialog_window = ctk.CTkToplevel(self.parent)
        self.dialog_window.title(self.title)
        window_width = 350
        window_height = 150
        screen_width = self.dialog_window.winfo_screenwidth()
        screen_height = self.dialog_window.winfo_screenheight()

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.dialog_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        pady = 5
        padx = 5
        self.dialog_window.lift()
        self.dialog_window.grab_set()
        self.custom_army_name = ctk.CTkLabel(self.dialog_window, text="Army-Name:")
        self.custom_army_name.grid(row=0, column=0, padx=padx, pady=pady, sticky="ew")

        self.custom_army_points = ctk.CTkLabel(self.dialog_window, text="Army Point-Limit:")
        self.custom_army_points.grid(row=1, column=0, padx=padx, pady=pady, sticky="ew")

        self.army_name_entry = ctk.CTkEntry(self.dialog_window)
        self.army_name_entry.insert(0, army_name.get())
        self.army_name_entry.grid(row=0, column=1, padx=padx, pady=pady, sticky="ew")

        self.army_point_limit_entry = ctk.CTkEntry(self.dialog_window)
        self.army_point_limit_entry.insert(0, army_points.get())
        self.army_point_limit_entry.grid(row=1, column=1, padx=padx, pady=pady, sticky="ew")

        self.button_frame = ctk.CTkFrame(self.dialog_window)
        self.ok_button = ctk.CTkButton(self.button_frame, text="OK", command=self.on_ok)
        self.ok_button.pack(side="left", padx=10, pady=0)

        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side="left", padx=10, pady=0)
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=5)

        self.dialog_window.grid_columnconfigure(0, weight=1)
        self.dialog_window.grid_columnconfigure(1, weight=1)

        self.dialog_window.grid_rowconfigure(0, weight=0)
        self.dialog_window.grid_rowconfigure(1, weight=0)
        self.dialog_window.grid_rowconfigure(2, weight=1)

    def on_ok(self):
        """Wird aufgerufen, wenn OK gedrückt wird"""
        self.result = (self.army_name_entry.get(), self.army_point_limit_entry.get())
        self.dialog_window.destroy()

    def on_cancel(self):
        """Wird aufgerufen, wenn Cancel gedrückt wird"""
        self.result = None
        self.dialog_window.destroy()


class UnitObject:
    def __init__(self,
                 name="",
                 is_general=False,
                 points=0,
                 starting_wounds_or_models=0,
                 lost_wounds_or_models=0,
                 is_fleeing=False,
                 standard_lost=False,
                 battle_standard_lost=False,
                 points_lost=0):
        self.name = name
        self.is_general = is_general
        self.points = points
        self.starting_wounds_or_models = starting_wounds_or_models
        self.lost_wounds_or_models = lost_wounds_or_models
        self.is_fleeing = is_fleeing
        self.standard_lost = standard_lost
        self.battle_standard_lost = battle_standard_lost
        self.points_lost = points_lost
        self.was_general = is_general

    def __getattr__(self, item):
        return

    def update_lost_points(self):
        self.points_lost = 0

        if self.is_general and self.lost_wounds_or_models == self.starting_wounds_or_models:
            self.points_lost += 100

        if int(self.lost_wounds_or_models) == int(self.starting_wounds_or_models):
            self.points_lost += int(self.points)
        elif self.is_fleeing and self.lost_wounds_or_models >= int(self.starting_wounds_or_models) / 2:
            self.points_lost += 0.75 * int(self.points)
        elif int(self.lost_wounds_or_models) >= int(self.starting_wounds_or_models) / 2:
            self.points_lost += 0.5 * int(self.points)

        if self.standard_lost:
            self.points_lost += 25

        if self.battle_standard_lost:
            self.points_lost += 100

        if self.standard_lost and self.battle_standard_lost:
            self.points_lost = self.points_lost - 25

        self.was_general = self.is_general

    def to_json(self):
        return {
            "name": self.name,
            "is_general": self.is_general,
            "points": self.points,
            "starting_wounds_or_models": self.starting_wounds_or_models,
            "current_wounds_or_models": self.current_wounds_or_models,
            "is_fleeing": self.is_fleeing,
            "standard_lost": self.standard_lost,
            "battle_standard_lost": self.battle_standard_lost
        }


def get_download_folder():
    if os.name == "nt":
        download_folder = Path(os.environ["USERPROFILE"]) / "Downloads"
    elif os.name == "posix":
        download_folder = Path.home() / "Downloads"
    else:
        download_folder = Path.home() / "Downloads"

    return download_folder


def import_file_new_recruit():
    global source_file_path
    file_path = filedialog.askopenfilename(
        title="Choose a source-file",
        initialdir=get_download_folder(),
        filetypes=(("Json-Files", "*.json"), ("All Files", "*.*"))
    )
    if file_path:
        source_file_path = file_path
        load_file_from_new_recruit()


def open_savefile():
    global savefile_path
    file_path = filedialog.askopenfilename(
        title="Choose a source-file",
        initialdir=get_download_folder(),
        filetypes=(("CSV-Files", "*.csv"), ("All Files", "*.*"))
    )
    if file_path:
        savefile_path = file_path
        load_army_from_savefile()


def load_file_from_new_recruit():
    global spent_points
    global army_points
    global army_name
    # Setup for every new run
    unit_costs.clear()
    name_counter.clear()
    unit_counter.clear()
    unit_counter_names.clear()
    general.clear()
    general_counter.clear()
    units.clear()
    army_name.set("")
    spent_points.set("0")
    army_points.set("0")

    if os.path.exists(source_file_path):

        with open(source_file_path, "r", encoding="utf-8") as file:

            if not file.name.endswith(".json"):
                messagebox.showerror("Error", "Invalid File-Type!")
                return

            data = json.load(file)
        convert_army(data)

    else:
        messagebox.showerror("Error", "File not Found!")
        return


def load_army_from_savefile():
    global spent_points
    global army_points
    global army_name
    global units
    # Setup for every new run
    unit_costs.clear()
    name_counter.clear()
    unit_counter.clear()
    unit_counter_names.clear()
    general.clear()
    general_counter.clear()
    units.clear()
    army_name.set("")
    spent_points.set("0")
    army_points.set("0")

    if os.path.exists(savefile_path):
        data = OrderedDict()
        if savefile_path.endswith(".csv"):
            csv_data = []
            with open(savefile_path, encoding="utf-8") as csvfile:
                reader = list(csv.reader(csvfile, delimiter=";"))

                if len(reader) > 1:
                    header = reader[0]
                    last_row = reader[-1]

                    if len(last_row) > 1:
                        army_name.set(last_row[0])
                        spent_points.set(last_row[1].replace("Total Points: ", "").strip().rstrip('0').rstrip('.'))
                        army_points.set(last_row[2].replace("/", "").strip().rstrip('0').rstrip('.'))
                        lost_points_total.set(last_row[4].strip().rstrip('0').rstrip('.'))
                for row in reader[1:-1]:
                    if len(row) < 5:
                        continue

                    name = row[0]
                    is_general = row[1].strip().lower() == "true"
                    points = int(row[2])
                    starting_wounds_or_models = int(row[3])
                    lost_wounds_or_models = int(row[4])

                    unit = UnitObject(
                        name=name,
                        is_general=is_general,
                        points=points,
                        starting_wounds_or_models=starting_wounds_or_models,
                        lost_wounds_or_models=lost_wounds_or_models
                    )

                    units[name] = unit

                row_index = 1
                for name, unit in units.items():
                    setup_unit_row(row_index, unit)
                    row_index += 1
        else:
            messagebox.showerror("Error", "Invalid File-Type!")
    else:
        messagebox.showerror("Error", "File not Found!")
        return


def convert_army(json_data):
    global army_name
    global army_points
    army_name.set(json_data["roster"]["name"])
    army_points.set(json_data["roster"]["costLimits"][0]["value"])
    army_selections = json_data["roster"]["forces"][0]["selections"]

    for army_selection in army_selections:
        if not army_selection["categories"][0]["name"] == "Uncategorized":
            process_selections(army_selection)
            process_wounds(army_selection)
            check_for_general(army_selection)

    print(army_name)
    for name, value in unit_costs.items():
        print(f"{name} : {value} pts | Wound/Unit-Size : {unit_counter[name]}  | General: {general[name]}")
        units[name] = (UnitObject(name, general[name], value, unit_counter[name], 0, False, False, False))
    points_spent = sum(unit_costs.values())
    spent_points.set(str(points_spent).rstrip('.0'))
    print(f"{spent_points} / {army_points.get()}")
    row_index = 1
    for name, unit in units.items():
        setup_unit_row(row_index, unit)
        row_index += 1


def process_wounds(army_selection):
    category = None
    if army_selection["name"] == "Special Characters":
        army_selection = army_selection["selections"][0]
    unit_name = army_selection["name"]
    highest_wounds = 1
    if "group" not in army_selection:
        category = army_selection.get("categories")
    else:
        highest_wounds = get_wounds(army_selection)
    selections = army_selection.get("selections", None)

    if not category or category[0]["name"] == "Lords" or category[0]["name"] == "Heroes":
        highest_wounds = get_wounds(army_selection)

        if isinstance(selections, list):
            if selections[0].get("selections", None):
                for selection in selections:
                    current_wound = get_wounds(selection)
                    if not current_wound:
                        current_wound = 0
                    if current_wound > highest_wounds:
                        highest_wounds = current_wound
                selections = selections[0]["selections"]
                for selection in selections:
                    current_wound = get_wounds(selection)
                    if not current_wound:
                        current_wound = 0
                    if current_wound > highest_wounds:
                        highest_wounds = current_wound

    else:
        model_wounds = get_wounds(army_selection)
        if not model_wounds:
            model_wounds = 0
        current_wounds = 0
        if isinstance(selections, list):

            for selection in selections:
                group = selection.get("group", None)
                unit_selections = selection.get("selections", None)
                crew_wounds = 0
                if unit_selections:
                    for unit_selection in unit_selections:
                        wounds = get_unit_strength(unit_selection)
                        if crew_wounds < wounds:
                            crew_wounds = wounds
                if not group:
                    highest_wounds = get_unit_strength(selection)
                    current_model_wounds = get_wounds(selection)
                    if current_model_wounds > model_wounds:
                        model_wounds = current_model_wounds

                if model_wounds > highest_wounds:
                    current_wounds = model_wounds
                elif highest_wounds > current_wounds:
                    current_wounds = highest_wounds
                if crew_wounds > highest_wounds and crew_wounds > model_wounds:
                    current_wounds = crew_wounds

        if model_wounds > highest_wounds:
            highest_wounds = model_wounds
        elif current_wounds > highest_wounds:
            highest_wounds = current_wounds

    if unit_name in unit_counter_names:
        count = unit_counter_names[unit_name] + 1
        unit_counter_names[unit_name] = count
        unit_name += " (" + str(count) + ")"

    else:
        unit_counter_names[unit_name] = 1

    unit_counter[unit_name] = highest_wounds


def process_selections(army_selection):
    if army_selection["name"] == "Special Characters":
        army_selection = army_selection["selections"][0]
    unit_name = army_selection["name"]
    total_cost = calculate_total_cost(army_selection)
    if total_cost > 0 and unit_name is not None:
        if unit_name in unit_counter:
            count = name_counter[unit_name] + 1
            name_counter[unit_name] = count
            unit_name += " (" + str(count) + ")"
        else:
            name_counter[unit_name] = 1
    unit_costs[unit_name] = total_cost


def calculate_total_cost(army_selection):
    total_cost = 0
    costs = army_selection.get("costs", 0)

    if isinstance(costs, list):
        for cost in costs:
            if cost["name"] == "pts":
                total_cost += float(cost["value"])

    selections = army_selection.get("selections", None)

    if isinstance(selections, list):
        for selection in selections:
            total_cost += calculate_total_cost(selection)

    return total_cost


def get_wounds(army_selection):
    profiles = army_selection.get("profiles", None)
    if not profiles or len(army_selection["profiles"]) == 0:
        selections = army_selection.get("selections", None)
        if selections:
            profiles = selections[0].get("profiles", None)
            if profiles:
                characteristics = profiles[0].get("characteristics", None)
                if not characteristics or len(characteristics) <= 5:
                    return 0
                else:
                    return int(characteristics[5].get("$text", 0))
        else:
            return 0
    else:
        characteristics = profiles[0].get("characteristics", None)
        if not characteristics or len(characteristics) <= 5:
            return 0
        else:
            return int(characteristics[5].get("$text", 0))


def get_unit_strength(selection):
    unit_strength = selection.get("number", None)
    if unit_strength:
        return int(unit_strength)
    else:
        return 0


def check_for_general(army_selection):
    if army_selection["name"] == "Special Characters":
        army_selection = army_selection["selections"][0]
    unit_name = army_selection["name"]

    is_general = False
    selections = army_selection.get("selections", None)
    if selections:
        for selection in selections:
            if selection["name"] == "General":
                is_general = True

    if unit_name in general:
        count = general_counter[unit_name] + 1
        general_counter[unit_name] = count
        general_name = army_selection["name"]
        general_name = general_name + " (" + str(count) + ")"
        general[general_name] = is_general
    else:
        general_counter[unit_name] = 1
        general_name = army_selection["name"]
        general[general_name] = is_general


def export_to_csv():
    global army_points
    global lost_points_total
    global spent_points
    global army_name
    army_file = army_name.get() + "-Army-Overview.csv"
    directory_path = filedialog.asksaveasfilename(title="Choose a destination",
                                                  defaultextension=".csv",
                                                  initialdir=get_download_folder(),
                                                  filetypes=[("CSV-Files", "*.csv")],
                                                  initialfile=army_file)
    file_path = directory_path
    file = open(file_path, "w")
    file.write("Name;General;Points;Star-Models/-Wounds;Models/Wounds lost\n")
    for name, unit in units.items():
        file.write(f"{name};")
        file.write(f"{str(unit.is_general)};")
        file.write(f"{unit.points};")
        file.write(f"{int(unit.starting_wounds_or_models)};")
        file.write(f"{int(unit.lost_wounds_or_models)}\n")

    file.write(
        f"{army_name.get()};Total Points: {spent_points.get()};/{army_points.get()};Lost:;{lost_points_total.get()};  \n")
    file.write(f"")
    success_message = f"CSV-File successfully saved to: {file_path}"
    print(success_message)
    messagebox.showinfo("Save successful", success_message)


def export_to_json():
    global army_points
    global lost_points_total
    global spent_points
    global army_name
    global units
    army_file = "NRAE-EXPORT-" + army_name.get() + "-Army-Overview.json"
    directory_path = filedialog.asksaveasfilename(title="Save as .json",
                                                  defaultextension=".json",
                                                  initialdir=get_download_folder(),
                                                  filetypes=[("JSON-Files", "*.json")],
                                                  initialfile=army_file)

    units_json_list = [unit.to_json() for unit in units.values()]

    army_data = {
        "army_name": army_name.get(),
        "army_points": army_points.get(),
        "current_points": spent_points.get(),
        "lost_points": lost_points_total.get(),
    }

    units_json_list.append(army_data)
    if directory_path:
        with open(directory_path, "w", encoding="utf-8") as file:
            json.dump(units_json_list, file, indent=4)
        success_message = f"JSON-File successfully saved in path: {directory_path}"
        print(success_message)
        messagebox.showinfo("Save successful", success_message)


# Setup for application
def setup_menu(root_pane):
    # Menu bar for point_calculator
    menu = CTkMenuBar(master=root_pane)
    file = menu.add_cascade("File")

    dropdown = CustomDropdownMenu(widget=file)
    dropdown.add_option(option="Load File", command=open_savefile)
    dropdown.add_option(option="Save File", command=export_to_csv)
    dropdown.add_separator()
    dropdown.add_option(option="Import File", command=import_file_new_recruit)
    dropdown.add_option(option="Export File", command=export_to_json)
    dropdown.add_separator()
    dropdown.add_option(option="Exit", command=root_pane.destroy)


def setup_window():
    global root
    global calculator_frame
    root.title("NewRecruit Point Calculator")
    root.wm_iconbitmap(icon_path)
    # Sets application non-resizable
    root.resizable(False, False)
    window_width = 1000
    window_height = 500

    # Calculate window position to center application on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Set appearance of application
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    setup_menu(root)

    main_frame = ctk.CTkFrame(root, bg_color="#2b2b2b")
    main_frame.pack(fill="both", expand=True)

    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=0)

    content_frame = ctk.CTkFrame(main_frame, bg_color="#2b2b2b")
    content_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

    canvas = tk.Canvas(content_frame, bg="#2b2b2b", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    calculator_frame = ctk.CTkFrame(canvas, bg_color="#2b2b2b", width=1100)
    canvas.create_window((0, 0), window=calculator_frame, anchor="nw")

    control_frame = ctk.CTkFrame(main_frame)
    control_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

    setup_control_frame(control_frame)

    def update_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    calculator_frame.bind("<Configure>", update_scroll_region)
    canvas.configure(yscrollcommand=scrollbar.set)

    calculator_frame.grid_columnconfigure(1, weight=1)
    calculator_frame.grid_columnconfigure(2, weight=1)
    calculator_frame.grid_columnconfigure(3, weight=1)
    calculator_frame.grid_columnconfigure(4, weight=1)
    calculator_frame.grid_columnconfigure(5, weight=1)
    calculator_frame.grid_columnconfigure(6, weight=1)
    calculator_frame.grid_columnconfigure(7, weight=1)
    calculator_frame.grid_columnconfigure(8, weight=1)
    calculator_frame.grid_columnconfigure(9, weight=1)
    calculator_frame.grid_columnconfigure(10, weight=1)

    setup_point_calculator_header(calculator_frame)
    setup_unit_row(1, UnitObject())

    def on_mouse_wheel(event):
        calculator_frame_height = calculator_frame.winfo_height()
        canvas_height = canvas.winfo_height()

        if calculator_frame_height > canvas_height:
            if event.delta > 0:
                canvas.yview_scroll(-1, "units")
            else:
                canvas.yview_scroll(1, "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    root.update_idletasks()

    root.mainloop()


def setup_point_calculator_header(content_frame):
    unit_name_label = ctk.CTkLabel(content_frame, text="Name")
    unit_name_label.grid(row=0, column=1, padx=5, pady=5)

    unit_general_label = ctk.CTkLabel(content_frame, text="General?")
    unit_general_label.grid(row=0, column=2, padx=5, pady=5)

    unit_points_label = ctk.CTkLabel(content_frame, text="Points")
    unit_points_label.grid(row=0, column=3, padx=5, pady=5)

    unit_starting_wound_or_model_label = ctk.CTkLabel(content_frame, text="Starting Wounds/Models")
    unit_starting_wound_or_model_label.grid(row=0, column=4, padx=5, pady=5)

    unit_current_wound_or_model_label = ctk.CTkLabel(content_frame, text="Lost Wounds/Models")
    unit_current_wound_or_model_label.grid(row=0, column=5, padx=5, pady=5)

    unit_fleeing_label = ctk.CTkLabel(content_frame, text="Fleeing?")
    unit_fleeing_label.grid(row=0, column=6, padx=5, pady=5)

    unit_standard_label = ctk.CTkLabel(content_frame, text="Standard lost?")
    unit_standard_label.grid(row=0, column=7, padx=5, pady=5)

    unit_battle_standard_label = ctk.CTkLabel(content_frame, text="Battle Standard lost?")
    unit_battle_standard_label.grid(row=0, column=8, padx=5, pady=5)

    unit_points_lost = ctk.CTkLabel(content_frame, text="Points lost")
    unit_points_lost.grid(row=0, column=9, padx=5, pady=5, sticky="w")

    delete_row_label = ctk.CTkLabel(content_frame, text="Delete Row")
    delete_row_label.grid(row=0, column=10, padx=5, pady=5, sticky="ew")


# Header-Row for the point-calculator
def setup_unit_row(row, unit: UnitObject):
    vcmd = (root.register(validate_input), "%S", "%P")

    unit_name_entry = ctk.CTkEntry(calculator_frame, border_width=1)
    unit_name_entry.grid(row=row, column=1, padx=5, pady=5)
    unit_name_entry._name = "unit_name_entry"

    unit_general_checkbox = ctk.CTkCheckBox(calculator_frame, text="", border_width=1, width=25,
                                            command=lambda: checkbox_update_unit(unit.name,
                                                                                 unit_general_checkbox))
    unit_general_checkbox.grid(row=row, column=2, padx=(unit_general_checkbox.cget("width")) / 2, pady=5)
    unit_general_checkbox._name = "unit_general_checkbox"

    unit_points_entry = ctk.CTkEntry(calculator_frame, border_width=1, validatecommand=vcmd, width=50)
    unit_points_entry.grid(row=row, column=3, padx=5, pady=5)
    unit_points_entry.bind("<KeyRelease>", lambda event: on_entry_change(event, unit.name, unit_points_entry))
    unit_points_entry._name = "unit_points_entry"

    unit_starting_wound_or_model_entry = ctk.CTkEntry(calculator_frame, border_width=1, validatecommand=vcmd, width=120)
    unit_starting_wound_or_model_entry.grid(row=row, column=4, padx=5, pady=5)
    unit_starting_wound_or_model_entry.bind("<KeyRelease>", lambda event: on_entry_change(event, unit.name,
                                                                                          unit_starting_wound_or_model_entry))
    unit_starting_wound_or_model_entry._name = "unit_starting_wound_or_model_entry"

    unit_lost_wound_or_model_entry = ctk.CTkEntry(calculator_frame, border_width=1, validatecommand=vcmd, width=120)
    unit_lost_wound_or_model_entry.grid(row=row, column=5, padx=5, pady=5)
    unit_lost_wound_or_model_entry.bind("<KeyRelease>", lambda event: on_entry_change(event, unit.name,
                                                                                      unit_lost_wound_or_model_entry))
    unit_lost_wound_or_model_entry._name = "unit_lost_wound_or_model_entry"

    unit_fleeing_checkbox = ctk.CTkCheckBox(calculator_frame, text="", border_width=1, width=25,
                                            command=lambda: checkbox_update_unit(unit.name,
                                                                                 unit_fleeing_checkbox))
    unit_fleeing_checkbox.grid(row=row, column=6, padx=(unit_general_checkbox.cget("width")) / 2, pady=5)
    unit_fleeing_checkbox._name = "unit_fleeing_checkbox"

    unit_standard_checkbox = ctk.CTkCheckBox(calculator_frame, text="", border_width=1, width=25,
                                             command=lambda: checkbox_update_unit(unit.name,
                                                                                  unit_standard_checkbox))
    unit_standard_checkbox.grid(row=row, column=7, padx=(unit_standard_checkbox.cget("width")) / 2, pady=5)
    unit_standard_checkbox._name = "unit_standard_checkbox"

    unit_battle_standard_checkbox = ctk.CTkCheckBox(calculator_frame, text="", border_width=1, width=30,
                                                    command=lambda: checkbox_update_unit(unit.name,
                                                                                         unit_battle_standard_checkbox))
    unit_battle_standard_checkbox.grid(row=row, column=8, padx=(unit_battle_standard_checkbox.cget("width")) / 2,
                                       pady=5)
    unit_battle_standard_checkbox._name = "unit_battle_standard_checkbox"

    unit_points_lost_var = ctk.StringVar(value=str(unit.points_lost))
    unit_points_lost_entry = ctk.CTkEntry(calculator_frame, border_width=1, width=60, textvariable=unit_points_lost_var)
    unit_points_lost_entry.grid(row=row, column=9, padx=5, pady=5)
    unit_points_lost_entry._name = "unit_points_lost_entry"

    unit.points_lost_var = unit_points_lost_var

    delete_row_button = ctk.CTkButton(calculator_frame, text="X", width=25,
                                      command=lambda: delete_row_from_grid(row, calculator_frame))
    delete_row_button.grid(row=row, column=10, padx=(unit_points_lost_entry.cget("width") / 2), pady=5, sticky="ew")

    unit_name_entry.insert(0, unit.name)
    if not unit.points == 0:
        unit_points_entry.insert(0, str(unit.points).rstrip('0').rstrip('.'))
    else:
        unit_points_entry.insert(0, "0")

    unit_starting_wound_or_model_entry.insert(0, str(unit.starting_wounds_or_models))
    unit_lost_wound_or_model_entry.insert(0, str(unit.lost_wounds_or_models))



    if unit.is_general:
        unit_general_checkbox.select()
    else:
        unit_general_checkbox.deselect()
    if unit.is_fleeing:
        unit_fleeing_checkbox.select()
    else:
        unit_fleeing_checkbox.deselect()
    if unit.standard_lost:
        unit_standard_checkbox.select()
    else:
        unit_standard_checkbox.deselect()
    if unit.battle_standard_lost:
        unit_battle_standard_checkbox.select()
    else:
        unit_battle_standard_checkbox.deselect()


def entry_update_unit(unit_name, entry: ctk.CTkEntry):
    global units
    if unit_name in units:
        if entry._name == "unit_starting_wound_or_model_entry":
            if not entry.get() == '':
                setattr(units[unit_name], "starting_wounds_or_models", int(entry.get()))
            else:
                setattr(units[unit_name], "starting_wounds_or_models", 0)
        elif entry._name == "unit_lost_wound_or_model_entry":
            if not entry.get() == '':
                setattr(units[unit_name], "lost_wounds_or_models", int(entry.get()))
            else:
                setattr(units[unit_name], "lost_wounds_or_models", 0)
        elif entry._name == "unit_points_entry":
            if not entry.get() == '':
                setattr(units[unit_name], "points", int(entry.get()))
            else:
                setattr(units[unit_name], "points", 0)

    calculate_points()


def checkbox_update_unit(unit_name, checkbox: ctk.CTkCheckBox):
    global units
    if unit_name in units:
        if checkbox._name == "unit_general_checkbox":
            setattr(units[unit_name], "is_general", bool(checkbox.get()))
        elif checkbox._name == "unit_fleeing_checkbox":
            setattr(units[unit_name], "is_fleeing", bool(checkbox.get()))
        elif checkbox._name == "unit_standard_checkbox":
            setattr(units[unit_name], "standard_lost", bool(checkbox.get()))
        elif checkbox._name == "unit_battle_standard_checkbox":
            setattr(units[unit_name], "battle_standard_lost", bool(checkbox.get()))

    calculate_points()


def calculate_points():
    global lost_points_total
    global units
    lost_points_total.set("0")
    for unit in units.values():
        unit.update_lost_points()

        if hasattr(unit, "points_lost_var"):
            unit.points_lost_var.set(str(unit.points_lost))
        if not lost_points_total.get() == "0":
            current_value = lost_points_total.get().rstrip('0').rstrip('.')
        else:
            current_value = 0
        lost_points_total.set(str(int(current_value) + int(unit.points_lost)).rstrip('0').rstrip('.'))


def on_entry_change(event, unit_name, widget):
    entry_update_unit(unit_name, widget)


def validate_input(char, value):
    if char.isdigit() or char == "":
        return True
    return False


def delete_row_from_grid(row_index, content_frame):
    if not row_index == 1:
        for widget in content_frame.grid_slaves(row=row_index):
            widget.grid_forget()

    for widget in content_frame.grid_slaves(row=1):
        if isinstance(widget, ctk.CTkEntry):
            widget.delete(0, tk.END)
            widget.insert(0, "")
        elif isinstance(widget, ctk.CTkCheckBox):
            widget.deselect()


def reset_grid():
    global lost_points_total
    global army_points
    global army_name
    global spent_points
    lost_points_total.set("0")
    army_points.set("0")
    army_name.set("")
    spent_points.set("")
    for widget in calculator_frame.winfo_children():
        widget.destroy()
    setup_point_calculator_header(calculator_frame)
    setup_unit_row(1, UnitObject())


# Unit-rows for the point-calculator
def setup_control_frame(control_frame):
    global spent_points
    global lost_points_total
    global army_points
    global army_name
    global calculator_frame

    control_frame.grid_columnconfigure(0, weight=0)
    control_frame.grid_columnconfigure(1, weight=0)
    control_frame.grid_columnconfigure(2, weight=0)
    control_frame.grid_columnconfigure(3, weight=1)
    control_frame.grid_columnconfigure(4, weight=1)
    control_frame.grid_columnconfigure(5, weight=0)
    control_frame.grid_columnconfigure(6, weight=0)
    control_frame.grid_columnconfigure(7, weight=0)
    control_frame.grid_columnconfigure(8, weight=0)
    control_frame.grid_columnconfigure(9, weight=0)
    control_frame.grid_columnconfigure(10, weight=0)

    button_width = 100
    button_height = 30
    # Left
    add_row_button = ctk.CTkButton(control_frame, text="Add Row", height=button_height, width=button_width,
                                   command=lambda: setup_unit_row(get_next_row_index(calculator_frame),
                                                                  UnitObject()))
    add_row_button.grid(row=0, column=0, padx=2.5, pady=0, sticky="w")

    load_to_units_button = ctk.CTkButton(control_frame, text="Load Army", height=button_height, width=button_width,
                                         command=lambda: load_custom_army_to_units(calculator_frame))
    load_to_units_button.grid(row=0, column=1, padx=2.5, sticky="w")

    reset_button = ctk.CTkButton(control_frame, text="Reset", fg_color="orange", text_color="black",
                                 height=button_height, width=button_width,
                                 command=reset_grid)
    reset_button.grid(row=0, column=2, padx=2.5, pady=0, sticky="w")

    # Middle
    army_title_label = ctk.CTkLabel(control_frame, text="Army: ")
    army_title_label.grid(row=0, column=3, padx=5, pady=0, sticky="e")

    army_name_label = ctk.CTkLabel(control_frame, textvariable=army_name)
    army_name_label.grid(row=0, column=4, padx=5, pady=0, sticky="w")

    # Right
    points_label = ctk.CTkLabel(control_frame, text="Army Points: ")
    points_label.grid(row=0, column=5, padx=5, pady=0, sticky="e")

    current_army_points = ctk.CTkLabel(control_frame, textvariable=spent_points)
    current_army_points.grid(row=0, column=6, padx=5, pady=0, sticky="e")

    point_spacer_label = ctk.CTkLabel(control_frame, text="/")
    point_spacer_label.grid(row=0, column=7, padx=0, pady=0, sticky="w")

    total_army_points = ctk.CTkLabel(control_frame, textvariable=army_points)
    total_army_points.grid(row=0, column=8, padx=5, pady=0, sticky="w")

    lost_points_label = ctk.CTkLabel(control_frame, text="|  Lost: ")
    lost_points_label.grid(row=0, column=9, padx=5, pady=0, sticky="e")

    lost_points_calculated = ctk.CTkLabel(control_frame, textvariable=lost_points_total)
    lost_points_calculated.grid(row=0, column=10, padx=5, pady=0, sticky="e")


def load_custom_army_to_units(frame):
    global units
    global army_name
    global army_points
    global spent_points
    units.clear()
    row_index = 1
    for row in range(row_index, (len(frame.grid_slaves()) // 8) + 1):
        widgets_in_row = [widget for widget in frame.grid_slaves(row=row)]
        widgets_in_row = sorted(widgets_in_row, key=lambda w: w.grid_info()["column"])

        entry_widgets = [w for w in widgets_in_row if isinstance(w, ctk.CTkEntry)]
        if entry_widgets:
            entry_widgets.pop()
        checkbox_widgets = [w for w in widgets_in_row if isinstance(w, ctk.CTkCheckBox)]

        if len(entry_widgets) == 4 and len(checkbox_widgets) == 4:
            name = entry_widgets[0].get()
            points = entry_widgets[1].get()
            starting_wounds_or_models = entry_widgets[2].get()
            lost_wounds_or_models = entry_widgets[3].get()

            is_general = checkbox_widgets[0].get()
            is_fleeing = checkbox_widgets[1].get()
            standard_lost = checkbox_widgets[2].get()
            battle_standard_lost = checkbox_widgets[3].get()

            if all([name, points, starting_wounds_or_models, lost_wounds_or_models]):
                units[name] = UnitObject(name, bool(is_general), points, starting_wounds_or_models,
                                         lost_wounds_or_models, bool(is_fleeing), bool(standard_lost),
                                         bool(battle_standard_lost))
                print(units[name].to_json())

    dialog = ArmyDetailDialog()
    root.wait_window(dialog.dialog_window)
    if dialog.result:
        army_name.set(dialog.result[0])
        army_points.set(dialog.result[1])
        spent_points_total = 0
        for unit in units.values():
            spent_points_total += float(unit.points)
        spent_points.set(str(spent_points_total).rstrip("0").rstrip("."))


def get_next_row_index(frame):
    highest_row = -1
    for widget in frame.grid_slaves():
        row = int(widget.grid_info()["row"])
        if row > highest_row:
            highest_row = row
    return highest_row + 1


def update_control_data():
    pass


setup_window()

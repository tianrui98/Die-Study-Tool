from abc import abstractmethod
from click import group
from sqlalchemy import all_
from src.objects import *
import src.progress as progress
from src.root_logger import *
import shutil
import tkinter as tk
from tkinter.constants import CENTER, RAISED, RIDGE, VERTICAL
from PIL import Image, ImageTk
import math
from tkinter import Toplevel, filedialog, messagebox
import os
import shutil
import json
from tkinter import font
from src.test import *
from datetime import datetime
from datetime import timedelta
from UI_group import GroupDisplay
from UI_pair import PairDisplay

#%% UI
class UI:
    def __init__(self, image_height_ratio = 0.7, project_name = "", project_address = "", progress_data = {},  group_display = False, root = None, testing_mode = False):
        # main interface
        if group_display:
            self.root = tk.Toplevel()
            self.mainUI = root
        else:
            self.root = tk.Tk()
            self.mainUI = None
        self.root.title("Die Study Tool")
        self.project_name = project_name
        self.project_address = project_address
        self.progress_data = progress_data
        self.part2 = part2
        self.demo_mode = False
        self.testing_mode = testing_mode
        self.quit = False

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.initial_width = int(self.screen_width * 0.8)
        self.initial_height = int(self.screen_height * 0.8)
        self.root.geometry("{}x{}".format(str(self.initial_width), str(self.initial_height)))
        self.root.minsize(width=self.initial_width, height=self.initial_height)

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=2)
        self.root.rowconfigure(2, weight=0)
        self.root.rowconfigure(3, weight=0)

        self.image_height_ratio = image_height_ratio
        self.image_height_char = self._pixel_to_char(int(self.initial_height * image_height_ratio))
        self.image_height_pixel = int(self.initial_height * image_height_ratio)
        self.button_frame_width = self.root.winfo_width() * 0.45
        self.button_frame_height = self.root.winfo_height() * 0.2
        self.identical_image_height_pixel = int(self.initial_height * 0.9 * 0.5)

        self.save_button_pressed_time = None
        self.save_recently_benchmark = timedelta(minutes = 1)

        self.test = Test()

#%% Shortcuts

    def _get_image_object(self, image_index):
        if image_index < len(self.cluster.images):
            return self.cluster.images[image_index]

    def _get_image_name (self, image_index):
        if image_index < len(self.cluster.images):
            return self.cluster.images[image_index].name

    def _get_image_address(self, image_index):
        if image_index < len(self.cluster.images):
            return os.path.join(self.project_address, self._get_image_name(image_index))

    def _swap_positions(self, l, pos1, pos2):

        # popping both the elements from list
        first_ele = l[pos1]
        second_ele = l[pos2]

        # inserting in each others positions
        l[pos2], l[pos1] = first_ele, second_ele
        return l

    def _pixel_to_char (self, pixel):
        f = font.Font(family = 'TkDefaultFont')
        font_size = f.measure('m')
        return int(pixel / font_size)
    def _char_to_pixel (self, char):
        f = font.Font(family = 'TkDefaultFont')
        font_size = f.measure('m')
        return int(char*font_size)
#%% Visuals and Aesthetics
    def add_image(self,  path, column, row, columspan, rowspan, parent, sticky="nsew", max_height = None, padx = 0, pady = 0):

        img = self.create_image_object(path, max_height)
        img_label = tk.Label(parent, image=img)
        img_label.image = img
        img_label.grid(column=column,
                       row=row,
                       columnspan=columspan,
                       rowspan=rowspan,
                       sticky=sticky, padx = padx, pady = pady)
        return img_label

    def create_image_object(self, path, max_height = None):
        image = Image.open(path)
        iw, ih = int(image.width), int(image.height)
        if not max_height:
            h = int(self.root.winfo_height() * self.image_height_ratio)

        else:
            h = max_height
        image = image.resize((math.ceil(h/ih * iw), h), Image. ANTIALIAS)
        img = ImageTk.PhotoImage(image)

        return img

    def create_darken_image_object(self, path, max_height = None):
        image_raw = Image.open(path)
        image = image_raw.point(lambda p : p *0.6)
        iw, ih = int(image.width), int(image.height)
        if not max_height:
            h = int(self.root.winfo_height() * self.image_height_ratio)

        else:
            h = max_height
        image = image.resize((math.ceil(h/ih * iw), h), Image. ANTIALIAS)
        img = ImageTk.PhotoImage(image)

        return img

    def add_icon(self, path, height, width,  column, row, columspan, rowspan, parent, sticky="nsew"):

        image = Image.open(path)
        image = image.resize((width, height), Image. ANTIALIAS)
        img = ImageTk.PhotoImage(image)
        img_label = tk.Label(parent, image=img)
        img_label.image = img
        img_label.grid(column=column,
                       row=row,
                       columnspan=columspan,
                       rowspan=rowspan,
                       sticky=sticky)
        return img_label

    def add_text(self, content, column, row, columspan, rowspan, parent, sticky="nsew"):
        text = tk.Label(parent, text=content)
        text.grid(column=column,
                  row=row,
                  columnspan=columspan,
                  rowspan=rowspan,
                  sticky=sticky)
        return text

    def add_button(self, content, func, height, width, column, row, columspan, rowspan, parent, sticky="nsew"):
        button_text = tk.StringVar()
        button = tk.Button(parent,
                           textvariable=button_text,
                           height=height,
                           width=width,
                           command=func,
                           font = ("Arial", "14"))
        button_text.set(content)
        button.grid(column=column,
                    row=row,
                    columnspan=columspan,
                    rowspan=rowspan,
                    sticky=sticky)

        return button

    def add_frame(self, height, width, column, row, columspan, rowspan, parent, sticky="nsew"):
        frame_width =width
        frame_height =height
        frame = tk.Frame(parent, bd=0, width = frame_height , height = frame_width, background= None)
        frame.grid(column=column,
                   row=row,
                   columnspan=columspan,
                   rowspan=rowspan,
                   sticky=sticky)

        return frame

    def add_filler(self, height, width, column, row, columspan, rowspan, parent, sticky="nsew", content = "", color = None):
        filler = tk.Label(parent, width=width, height=height, text = content, bg = color)
        filler.grid(column=column,
                    row=row,
                    columnspan=columspan,
                    rowspan=rowspan,
                    sticky=sticky)

        return filler

    def change_button_color (self, button_widget, new_fg = "black", new_font = ("Arial", "14")):
        button_widget.config (fg = new_fg, font = new_font)

    def activate_button (self, button_widget):
        self.change_button_color (button_widget, new_fg = "#dda15e", new_font = ("Arial", "14", "bold"))

    def deactivate_button (self, button_widget):
        self.change_button_color (button_widget, new_fg = "black", new_font = ("Arial", "14"))

#%% Actions

    def open_first_cluster(self):
        """Open the first cluster in stage 0.
        Create a Cluster object

        Return: Cluster object
        """
        all_clusters = [c for c in self.progress_data[self.project_name]["clusters"] if c != "Singles"]
        cluster_name =  sorted(all_clusters, key= lambda s: s.split("_")[0])[0]

        #create cluster object
        images = self.progress_data[self.project_name]["clusters"][cluster_name]["images"]
        return Cluster(cluster_name = cluster_name, images = images, best_image_name = None, matches = set(), nomatches = set())

    def open_demo_project (self):
        self.demo_mode = True
        dirname="demo"
        self.project_name = "demo"
        self.project_address, self.progress_data = progress.start_new_project(dirname, self.project_name)
        self.stage = Stage(0, self.progress_data[self.project_name])
        if self.testing_mode:
            self.test = Test(self.progress_data[self.project_name]["clusters"]["Singles"]["images"])
        #open the first cluster
        self.cluster = self.open_first_cluster()

        #initialize image display
        self.refresh_image_display()

        #close pop-up
        self.open_window.quit()
        self.open_window.destroy()

        logger.info(f"_____create demo project_____")
        return None

    def choose_project(self):
        self.progress_data = progress.checkout_progress()
        existing_projects = set(self.progress_data.keys())
        if not existing_projects:
            return
        self.create_choose_project_window(existing_projects)
        self.project_address = os.path.join(os.getcwd(), "projects", self.project_name)

        self.progress_data, self.stage, self.cluster = progress.load_progress(self.project_name)
        if self.testing_mode:
            self.test = Test(self.progress_data[self.project_name]["clusters"]["Singles"]["images"])

        logger.info(f"Open project {self.project_name} at stage {self.stage.stage_number} ")
        if self.stage.stage_number < 3:
            self.refresh_image_display()
        else:
            #start identical UI
            self.start_identical_UI()

    def browse_files(self):
        """Let user choose which new project/folder to start working on
        pass the directory name to the class
        show images
        """
        dirname = filedialog.askdirectory(parent=self.root)

        if not dirname:
            return 
        #check if the folder is valid
        valid = True
        for folder in os.listdir(dirname):
            if not folder.startswith("."):
                is_folder = os.path.isdir(dirname + "/" + folder)
                no_dot = "." not in folder
                valid = valid and is_folder and no_dot

        valid = valid and "Singles" in os.listdir(dirname)

        if not valid:
            messagebox.askokcancel("Invalid folder", "The folder you have chosen is not valid. \nIt should contain cluster folders and a 'Singles' folder and nothing else." )
            return None

        self.project_name = os.path.basename(dirname)
        self.project_address, self.progress_data = progress.start_new_project(dirname, self.project_name)
        self.stage = Stage(0, self.progress_data[self.project_name])
        if self.testing_mode:
            self.test = Test(self.progress_data[self.project_name]["clusters"]["Singles"]["images"])
        #open the first cluster
        self.cluster = self.open_first_cluster()

        #refresh image display
        self.refresh_image_display()

        #close pop-up
        self.open_window.destroy()

        logger.info("_____Create new project {}_____".format(self.project_name))
        return None
    
    def save(self):
        """save results to data.json
        """
        if len(self.progress_data) > 0:
            logger.info("====SAVE====\n\n")
            progress.save_progress_data_midway(self.project_name, self.stage, self.cluster, self.progress_data)
            self.save_button_pressed_time = datetime.now()

    def exit(self):
        #wipe out records at exit for demo projects
        if self.demo_mode:
            progress.clear_current_project(self.project_name, self.progress_data)
        else:
            if len(self.progress_data) == 0:
                progress.clear_current_project(self.project_name, self.progress_data)
            elif self.save_button_pressed_time and datetime.now() - self.save_button_pressed_time < self.save_recently_benchmark:
                pass
            else:
                keep_progress = messagebox.askyesno("Exit", "Save your project?" )
                if keep_progress:
                    progress.save_progress_data_midway(self.project_name, self.stage, self.cluster,self.progress_data)
                else:
                    progress.clear_current_project(self.project_name, self.progress_data)
        logger.info(str(self.progress_data))
        logger.info("====EXIT====\n\n")
        self.root.quit()
        self.root.destroy()
        if self.part2:
            self.mainUI.destroy()
        self.quit = True

    def export_data(self, keep_progress = False):
        save_address = filedialog.askdirectory() # asks user to choose a directory
        if not save_address:
            return None
        self.progress_data, _ = progress.update_progress_data(self.project_name, self.stage, self.cluster, self.progress_data)
        res, destination_address = progress.export_results(self.project_name,self.progress_data, save_address, keep_progress)
        if self.testing_mode:
            self.test.test_export(self.progress_data[self.project_name]["clusters"], self.project_name, destination_address)
        if not keep_progress:
            #wipe out the records in progress data
            progress.clear_current_project(self.project_name, self.progress_data)

        logger.info("====EXPORTED RESULTS====")
        if not keep_progress:
            self.root.destroy()
            if self.mainUI:
                self.mainUI.destroy()
            self.quit = True

    def export(self, project_completed = False):
        if project_completed:
            response = self.create_export_results_window()
            if response:
                self.export_data()
        else:
            response = messagebox.askokcancel("Export intermediate results", "You have NOT completed the current project.\nExport the intermediate results?" )
            if response:
                keep_progress = messagebox.askyesno("Export intermediate results", "Keep your current progress in the system ?" )
                self.export_data(keep_progress)
        return response

    def create_export_results_window(self):
        response = messagebox.askokcancel("Export results", "You have completed the current project.\nExport the results?" )
        return response

    def create_save_progress_window(self, message):
        response = messagebox.askokcancel("Save progress", message + "\nMove on to the next?" )
        return response

    def create_open_window(self):
        self.open_window = Toplevel(self.root)
        self.open_window.title("Open")
        self.open_window.geometry("300x200")
        self.demo_project_button = tk.Button(self.open_window, text="   Start demo project   ", command = self.open_demo_project)
        self.demo_project_button.place(relx=0.5, rely=0.2, anchor=CENTER)
        self.new_project_button = tk.Button(self.open_window, text="   Start a new project   ", command = self.browse_files)
        self.new_project_button.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.continue_existing_project = tk.Button(self.open_window, text="Continue existing project", command = self.choose_project)
        self.continue_existing_project.place(relx=0.5, rely=0.6, anchor=CENTER)
        self.open_window.mainloop()

    def create_choose_project_window(self, choices):
        self.choose_project_window = Toplevel(self.root)
        self.choose_project_window.title("Choose a project")
        self.choose_project_window.geometry("200x300")

        name = tk.StringVar()
        default_project_name = list(choices)[0]
        name.set(default_project_name)

        popupMenu = tk.OptionMenu(self.choose_project_window, name, *choices)
        popupMenu.place(relx=0.5, rely=0.3, anchor=CENTER)

        def exit():
            self.choose_project_window.quit()
            self.choose_project_window.destroy()
            self.open_window.quit()
            self.open_window.destroy()

        self.project_name = name.get()
        ok_button = tk.Button(self.choose_project_window, text = "OK", command = exit)
        ok_button.place(relx=0.5, rely=0.8, anchor=CENTER)
        self.choose_project_window.mainloop()

    def create_UI(self):
        #initialize left and right images
        self.left_image = self.add_image(os.path.join("images","blank.png"), 0, 1, 1, 1, self.root, "w", self.image_height_pixel, 0, 0)
        self.right_image = self.add_image(os.path.join("images","blank.png"), 1, 1, 1, 1, self.root, "w", self.image_height_pixel, 0, 0)

        # menu bar
        right_menu_bar = self.add_frame(self.button_frame_height, self.button_frame_width, 1, 0, 1, 1, self.root, "e")
        self.open_btn = self.add_button("Open", self.create_open_window, 2, 3, 1, 0, 1, 1, right_menu_bar, sticky = "e")
        self.export_btn = self.add_button("Export", self.export, 2, 3, 2, 0, 1, 1, right_menu_bar, sticky = "e")
        self.save_btn = self.add_button("Save", self.save, 2, 3, 3, 0, 1, 1, right_menu_bar, sticky = "e")
        self.deactivate_button(self.save_btn) #TODO activate it later
        self.exit_btn = self.add_button("Exit", self.exit, 2, 3, 4, 0, 1, 1, right_menu_bar, sticky = "e")

        left_menu_bar = self.add_frame(self.button_frame_height, self.button_frame_width,0, 0, 1, 1, self.root, "we")
        # left_menu_bar.columnconfigure(1, weight=1)
        self.project_title_label = self.add_text("Project Title: ", 0, 0, 1, 1, left_menu_bar, sticky= "w")
        self.stage_label = self.add_text("Current Stage: ", 0, 1, 1, 1, left_menu_bar, sticky= "w")

        # image info
        self.left_info_bar = self.add_frame(self.button_frame_height, self.button_frame_width,0, 2, 1, 1, self.root)

        # self.left_image_name_label = self.add_text("Name : ", 0, 0, 1, 1, self.left_info_bar, sticky= "w")
        # self.left_cluster_label = self.add_text("Cluster : ", 0, 1, 1, 1, self.left_info_bar, sticky= "w")
        # _ = self.add_filler(4, 4, 2, 0, 1, 2, self.left_info_bar, "e", "", None)

        self.right_info_bar = self.add_frame(self.button_frame_height, self.button_frame_width,1, 2, 1, 1, self.root, "we")
        # self.right_info_bar.grid_propagate(0)
        # self.right_info_bar.columnconfigure(2, weight=1)


        # self.right_image_name_label = self.add_text("Name : ", 0, 0, 1, 1, self.right_info_bar, sticky="w")
        # self.right_cluster_label = self.add_text("Cluster : ", 0, 1, 1, 1, self.right_info_bar, sticky="w")

        # self.right_tick =self.add_image(os.path.join("images","blank.png"), 1, 0, 1, 1, self.right_info_bar, "w", 15, 0, 0)

        #navigation buttons
        # self.prev_btn = self.add_button("◀", self.load_prev_image, 4, 4, 2, 0, 1, 2, self.right_info_bar, sticky="e")
        # self.next_btn = self.add_button("▶", self.load_next_image, 4, 4, 3, 0, 1, 2, self.right_info_bar, sticky="e")

        # action buttons
        action_bar = self.add_frame(self.button_frame_height, self.button_frame_width,1, 3, 1, 1, self.root, "se")
        # action_bar.rowconfigure(0, weight=1)
        # for i in range(4):
        #     action_bar.columnconfigure(i, weight=1)

        # action_button_height = 4

        # self.best_image_btn = self.add_button("Best Image", self.mark_best_image, action_button_height, 8, 0, 0, 1, 1, action_bar,"se")
        # self.no_match_btn = self.add_button("No Match", self.mark_no_match, action_button_height, 8, 1, 0, 1, 1, action_bar, "se")
        # self.match_btn = self.add_button("Match", self.mark_match, action_button_height, 8, 2, 0, 1, 1, action_bar, "se")

    def start(self):
        self.create_UI()
        try:
            self.root.mainloop()
        except:
            logger.error("====Error in main loop====")
            logger.error(f"progress_data{self.progress_data}")

# %%

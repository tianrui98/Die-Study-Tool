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
#%% UI
class UI:
    def __init__(self, image_height_ratio, project_name = "", project_address = "", progress_data = {}):
        # main interface
        self.root = tk.Tk()
        self.root.title("Die Study Tool")
        self.project_name = project_name
        self.project_address = project_address
        self.progress_data = progress_data
        self.demo_mode = False

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

        self.image_height_char = self._pixel_to_char(int(self.initial_height * image_height_ratio))
        self.image_height_pixel = int(self.initial_height * image_height_ratio)
        self.button_frame_width = self.root.winfo_width() * 0.45
        self.button_frame_height = self.root.winfo_height() * 0.2
        self.identical_image_height_pixel = int(self.initial_height * 0.9 * 0.5)

#%% Shortcuts

    def _get_image_object(self, image_index):
        if image_index < len(self.cluster.images):
            return self.cluster.images[image_index]

    def _get_image_name (self, image_index):
        if image_index < len(self.cluster.images):
            return self.cluster.images[image_index].name

    def _open_cluster(self, project_address):
        """Open an unfinished cluster.
        Create a Cluster object

        Return: Cluster object
        """
        all_clusters = [f for f in os.listdir(project_address) if not f.startswith('.')]
        cluster_name =  all_clusters[0]
        cluster_address = os.path.join(project_address, cluster_name )

        #create cluster object
        return Cluster(folder_address = cluster_address)

    def _swap_positions(self, list, pos1, pos2):

        # popping both the elements from list
        first_ele = list.pop(pos1)
        second_ele = list.pop(pos2-1)

        # inserting in each others positions
        list.insert(pos1, second_ele)
        list.insert(pos2, first_ele)

        return list

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

        image = Image.open(path)
        iw, ih = int(image.width), int(image.height)
        if not max_height:
            h = int(self.root.winfo_height() * self.image_height_ratio)

        else:
            h = max_height
        image = image.resize((math.ceil(h/ih * iw), h), Image. ANTIALIAS)
        img = ImageTk.PhotoImage(image)
        img_label = tk.Label(parent, image=img)
        img_label.image = img
        img_label.grid(column=column,
                       row=row,
                       columnspan=columspan,
                       rowspan=rowspan,
                       sticky=sticky, padx = padx, pady = pady)
        return img_label


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

    def open_demo_project (self):
        dirname = "demo"
        self.demo_mode = True
        self.project_name = dirname.split("/")[-1]
        self.project_address, self.progress_data = progress.start_new_project(dirname, self.project_name)
        self.stage = Stage(0, self.project_address)

        #open the first cluster
        self.cluster = self._open_cluster(project_address = self.project_address)

        #read or make Singles folder
        if not os.path.exists(dirname + "/" + "Singles"):
            os.mkdir(dirname + "/" + "Singles")
        self.singles = Cluster( str(dirname + "/" + "Singles"))

        #initialize image display
        self.initialize_image_display()

        #close pop-up
        self.open_window.destroy()

        logger.info("_____Create demo project{}_____".format(self.project_name))
        return None

    def choose_project(self):

        self.progress_data = progress.checkout_progress()
        existing_projects = {d.split('/')[-1] for d in list(self.progress_data.keys())}
        if not existing_projects:
            return
        self.create_choose_project_window(existing_projects)
        self.project_address = os.getcwd() + "/projects/" + self.project_name

        self.progress_data, self.stage, self.cluster = progress.load_progress(self.project_address)
        self.singles = Cluster( str(self.project_address+ "/" + "Singles"))

        self.initialize_image_display()

        logger.info("Open existing project {}".format(self.project_name))

    def browse_files(self):
        """Let user choose which new project/folder to start working on
        pass the directory name to the class
        show images
        """

        #TODO: allow user to give project a name
        dirname = filedialog.askdirectory(parent=self.root)

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

        self.project_name = dirname.split("/")[-1]
        self.project_address, self.progress_data = progress.start_new_project(dirname, self.project_name)
        self.stage = Stage(0, self.project_address)

        #open the first cluster
        self.cluster = self._open_cluster(project_address = self.project_address)

        #read or make Singles folder
        if not os.path.exists(dirname + "/" + "Singles"):
            os.mkdir(dirname + "/" + "Singles")
        self.singles = Cluster( str(dirname + "/" + "Singles"))

        #initialize image display
        self.initialize_image_display()

        #close pop-up
        self.open_window.destroy()

        logger.info("_____Create new project{}_____".format(self.project_name))
        return None

    def initialize_image_display(self) -> None:
        pass

    def load_next_image (self) -> None:
        pass

    def load_prev_image (self) -> None:
        pass

    def mark_match (self):
        pass

    def mark_validation_no_match (self):
        pass

    def mark_identical (self):
        pass

    def mark_best_image (self):
        pass

    def check_completion_and_move_on (self):
        """This function is called when user clicks "next" while at the last image
        !!! only mark cluster complete if user clicks ok"""

        if progress.check_cluster_completion(self.cluster,self.stage):
            self.stage = progress.mark_cluster_completed(self.cluster, self.stage)

        if progress.check_project_completion(self.stage):
            logger.info("!!!!project complete!!!!")
            logger.info(str(self.progress_data))
            self.export_btn()
            self.stage = progress.unmark_cluster_completed(self.cluster, self.stage)
        else:
            if progress.check_stage_completion(self.stage):
                message = "You have completed the current *STAGE*."
                logger.info("_____STAGE {} COMPLETED_____".format(self.stage.name))
            else:
                if progress.check_cluster_completion(self.cluster, self.stage):
                    message = "You have completed the current cluster."
                else:
                    return None

            response = self.create_save_progress_window(message)
            if response:
                self.stage = progress.mark_cluster_completed(self.cluster, self.stage)

                self.progress_data, self.cluster, self.stage = progress.update_folder_and_record(self.progress_data, self.project_address, self.cluster, self.stage)
                progress.check_completion_and_save(self.cluster, self.stage, self.project_address, self.progress_data)
                self.progress_data, self.stage, self.cluster = progress.load_progress(self.project_address)

                if self.cluster:
                    #if next cluster has only 1 image, skip it & recurse
                    if len(self.cluster.images) <= 1:
                        logger.info("----SKIP {}----".format(self.cluster.name))
                        self.stage = progress.mark_cluster_completed(self.cluster,self.stage)
                        self.progress_data, self.cluster, self.stage = progress.update_folder_and_record(self.progress_data, self.project_address, self.cluster, self.stage)
                        progress.check_completion_and_save(self.cluster, self.stage, self.project_address, self.progress_data)
                        self.progress_data, self.stage, self.cluster = progress.load_progress(self.project_address)
                        self.check_completion_and_move_on ()
                    else:
                        self.initialize_image_display()
                if "stage" in message:
                    logger.info(str(self.progress_data))
            else:
                self.stage = progress.unmark_cluster_completed(self.cluster, self.stage)

    def save(self):
        """save results
        """
        if len(self.progress_data) > 0:
            self.progress_data, self.cluster, self.stage = progress.update_folder_and_record(self.progress_data, self.project_address, self.cluster,self.stage)
            progress.check_completion_and_save(self.cluster, self.stage, self.project_address, self.progress_data)

    def exit(self):
        #wipe out records at exit for demo projects
        if self.demo_mode:
            if self.project_address in self.progress_data:
                _ = self.progress_data.pop(self.project_address)
            data_file = open("data.json", "w")
            json.dump(self.progress_data, data_file)
            data_file.close()
            shutil.rmtree(self.project_address)
        else:
            if len(self.progress_data) > 0:
                self.save()
            else:
                shutil.rmtree(self.project_address)

        logger.info(str(self.progress_data))
        logger.info("====EXIT====\n\n")
        self.root.destroy()

    def export(self, keep_progress = False):
        save_address = filedialog.askdirectory() # asks user to choose a directory
        if not save_address:
            return None
        self.progress_data, self.cluster, self.stage = progress.update_folder_and_record(self.progress_data, self.project_address, self.cluster, self.stage)
        progress.check_completion_and_save(self.cluster, self.stage, self.project_address, self.progress_data)
        self.progress_data, _, _ = progress.load_progress(self.project_address, False)
        progress.export_results(self.project_address,self.progress_data, save_address, keep_progress)
        logger.info("====EXPORT====")
        self.root.destroy()


    def export_btn(self):
        project_completed = progress.check_project_completion(self.stage)
        if project_completed:
            response = self.create_export_results_window()
            if response:
                self.export()

        else:
            response = messagebox.askokcancel("Export intermediate results", "You have NOT completed the current project.\nExport the intermediate results?" )
            keep_progress = messagebox.askyesno("Export intermediate results", "Keep your current progress in the system ?" )
            if response:
                self.export(keep_progress)
                if not keep_progress:
                    self.root.destroy()

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

    def start (self):
        pass

    def create_UI (self):
        pass

# %%

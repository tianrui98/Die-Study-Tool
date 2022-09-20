from src.objects import *
import src.progress as progress
from src.root_logger import *
import tkinter as tk
from tkinter.constants import CENTER, RAISED, RIDGE, VERTICAL
from PIL import Image, ImageTk
import math
from tkinter import Toplevel, filedialog, messagebox
import os
from tkinter import font
from src.test import *
from datetime import datetime
from datetime import timedelta

#%% UI
class UI():
    def __init__(self, image_height_ratio = 0.7, project_name = "", project_address = "", progress_data = {},  group_display = False, root = None, testing_mode = False):
        super().__init__()
        # main interface
        self.root = tk.Tk()
        self.root.title("Die Study Tool")
        self.project_name = project_name
        self.project_address = project_address
        self.progress_data = progress_data
        self.demo_mode = False
        self.testing_mode = testing_mode
        self.quit = False
        self.existing_project_names = progress.get_existing_project_names()

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.initial_width = int(self.screen_width * 0.8)
        self.initial_height = int(self.screen_height * 0.8)
        self.root.geometry("{}x{}".format(str(self.initial_width), str(self.initial_height)))
        self.root.minsize(width=self.initial_width, height=self.initial_height)

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)

        self.image_height_ratio = image_height_ratio
        self.image_height_char = self._pixel_to_char(int(self.initial_height * image_height_ratio))
        self.image_height_pixel = int(self.initial_height * image_height_ratio)
        self.button_frame_width = self.root.winfo_width() * 0.45
        self.button_frame_height = self.root.winfo_height() * 0.2
        self.display_frame_width = self.root.winfo_width() * 0.9
        self.display_frame_height = self.root.winfo_height() * 0.8
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

    def _image_name_to_address(self, image_name):
        return os.path.join(self.project_address, image_name)

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

    def add_filler(self, height, width, column, row, columspan, rowspan, parent, sticky="nsew", content = "", color = "red"):
        filler = tk.Label(parent, width=width, height=height, text = content, bg = color)
        filler.grid(column=column,
                    row=row,
                    columnspan=columspan,
                    rowspan=rowspan,
                    sticky=sticky)

        return filler

#%% Actions in the Main UI

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
        dirname="images/demo"
        self.project_name = "demo"
        self.project_address, self.progress_data = progress.start_new_project(dirname, self.project_name)
        self.stage = Stage(0, self.progress_data[self.project_name])
        if self.testing_mode:
            self.test = Test(self.progress_data[self.project_name]["clusters"]["Singles"]["images"])
        #open the first cluster
        self.cluster = self.open_first_cluster()

        #initialize image display
        self.group_frame_start()
        self.group_frame_refresh_image_display()

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
        self.open_chosen_project()

    def open_chosen_project(self):
        self.project_address = os.path.join(os.getcwd(), "projects", self.project_name)
        self.progress_data, self.stage, self.cluster, unprocessed_marked_coin_group_list = progress.load_progress(self.project_name)
        if self.testing_mode:
            self.test = Test(self.progress_data[self.project_name]["clusters"]["Singles"]["images"])
            self.test.load_project_into_test(self.progress_data[self.project_name]["clusters"])
        logger.info(f"Open project {self.project_name} at stage {self.stage.name} ")
        if self.stage.stage_number == 0 or self.stage.stage_number == 3:
            self.group_frame_start()
            self.marked_coin_group_list = unprocessed_marked_coin_group_list
            
            for coin_list, _ in unprocessed_marked_coin_group_list:
                #process coin list
                for coin in coin_list:
                    self.marked_added_coin_dict[coin] = self.create_image_object(self._image_name_to_address(coin))
            self.group_frame_refresh_image_display()
        else:
            if self.testing_mode:
                current_cluster = self.progress_data[self.project_name]["stages"][str(self.stage.stage_number)]["current_cluster"]["name"]
                if self.stage.stage_number == 1:
                    current_cluster_best_image_name = self.progress_data[self.project_name]["clusters"][current_cluster]["best_image_name"]
                else:
                    current_cluster_best_image_name = current_cluster
                for coin in self.progress_data[self.project_name]["stages"][str(self.stage.stage_number)]["current_cluster"]["unprocessed_matches"]:
                    self.test.match(current_cluster_best_image_name, coin, self.stage.stage_number)
                for coin in self.progress_data[self.project_name]["stages"][str(self.stage.stage_number)]["current_cluster"]["unprocessed_nomatches"]:
                    self.test.unmatch(current_cluster_best_image_name, coin, self.stage.stage_number)        
            self.pair_frame_start()
            self.pair_frame_refresh_image_display()
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

        #create frames based on the stage
        if self.stage.stage_number == 0 or self.stage.stage_number == 3:
            self.group_frame_start()
            self.group_frame_refresh_image_display()
        else:
            self.pair_frame_start()
            self.pair_frame_refresh_image_display()

        #close pop-up
        self.open_window.destroy()

        logger.info("_____Create new project {}_____".format(self.project_name))
        return None
    
    def save_progress_midway(self):
        if self.stage.stage_number == 0 or self.stage.stage_number == 3:
            marked_coin_group_list = self.marked_coin_group_list
        else:
            marked_coin_group_list = None
        self.progress_data, self.stage = progress.save_progress_data_midway(self.project_name, self.stage, self.cluster, self.progress_data, marked_coin_group_list)
    
    def save(self):
        """save results to data.json
        """
        if len(self.progress_data) > 0:
            logger.info("====SAVE====\n\n")
            self.save_progress_midway()
            stages = self.progress_data[self.project_name]["stages"]
            self.save_button_pressed_time = datetime.now()
            self.existing_project_names.add(self.project_name)

    def exit(self):
        #wipe out records at exit for demo projects
        if len(self.project_name) == 0:
            pass
        elif self.demo_mode:
            progress.clear_current_project(self.project_name, self.progress_data)
        else:
            if len(self.progress_data) == 0:
                progress.clear_current_project(self.project_name, self.progress_data)
            elif self.save_button_pressed_time and datetime.now() - self.save_button_pressed_time < self.save_recently_benchmark:
                pass
            else:
                keep_progress = messagebox.askyesno("Exit", "Save your project?" )
                if keep_progress:
                    self.save_progress_midway()
                    logger.info("====SAVE====\n\n")
                elif self.project_name not in self.existing_project_names:
                    progress.clear_current_project(self.project_name, self.progress_data)
        logger.info(str(self.progress_data))
        logger.info("====EXIT====\n\n")
        self.root.quit()
        self.root.destroy()
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
            self.quit = True

    def export(self, project_completed = False):
        if project_completed:
            response = self.create_export_results_window()
            if response:
                self.export_data()
        else:
            response = messagebox.askokcancel("Export intermediate results", "You have NOT completed the current project.\nExport the intermediate results?" )
            if response:
                keep_progress = messagebox.askyesno("Export intermediate results", "Keep the project in the system ?" )
                self.export_data(keep_progress)
        return response

    def browse_directory_for_import(self):
        dirname = filedialog.askdirectory(parent=self.import_window)
        if not dirname:
            return 
        elif not os.path.isdir(dirname):
            return
        else:
            self.imported_image_folder_address_text_box.insert("end", dirname)
            self.imported_image_folder_address_var.set(dirname)
            return 

    def browse_file_for_import(self):
        filename = filedialog.askopenfilename(parent = self.import_window)
        if not filename:
            return
        elif ".json" not in filename:
            return
        else:
            self.imported_data_file_address_text_box.insert("end", filename)
            data_file = open(filename, "r")
            self.imported_data_var.set(data_file.read())
            data_file.close()
            
            #add project names to the optionmenu
            imported_project_names = eval(self.imported_data_var.get()).keys()
            
            if len(imported_project_names) > 0:
                for project_name in imported_project_names:
                    self.imported_project_name_option_box["menu"].add_command(label = project_name, command = tk._setit(self.imported_project_name_var, project_name))
            if len(imported_project_names) == 1:
                self.imported_project_name_var.set(list(imported_project_names)[0])
            return 

    def create_import_window(self):
        self.import_window = Toplevel(self.root)
        self.import_window.title("Import a project")
        self.import_window.geometry(f"{self.initial_width // 2}x{self.initial_height // 2}")

        self.imported_data_var = tk.StringVar()
        self.imported_data_var.set("{}")
        self.imported_image_folder_address_var = tk.StringVar()
        self.imported_image_folder_address_var.set("")
        self.imported_project_name_var = tk.StringVar()
        self.imported_project_name_var.set("")
        relx_base = 0.2
        rely_base = 0.2

        data_file_address_text = tk.Label(self.import_window, text="Data file (.json) address:")
        data_file_address_text.place(relx = relx_base, rely = rely_base, anchor = "w")
        self.imported_data_file_address_text_box = tk.Text(self.import_window, width = self._pixel_to_char(int((self.initial_width // 2) * 0.8)), height = 2)
        self.imported_data_file_address_text_box.place(relx=relx_base, rely=rely_base + 0.1, anchor= "w")
        data_file_open_button = tk.Button(self.import_window, text="Browse", command = self.browse_file_for_import)
        data_file_open_button.place(relx = relx_base * 4, rely = rely_base + 0.1, anchor = "w")

        imported_project_name_text = tk.Label(self.import_window, text="Project name:")
        imported_project_name_text.place(relx = relx_base, rely = rely_base *2, anchor = "w")

        self.imported_project_name_option_box = tk.OptionMenu(self.import_window, self.imported_project_name_var, None)
        self.imported_project_name_option_box.configure(width = 20)
        self.imported_project_name_option_box.place(relx=relx_base, rely=rely_base *2 + 0.1, anchor = "w")
        
        imported_image_folder_address_text = tk.Label(self.import_window, text="Image folder address:")
        imported_image_folder_address_text.place(relx = relx_base, rely = rely_base *3 , anchor = "w")
        self.imported_image_folder_address_text_box = tk.Text(self.import_window, width = self._pixel_to_char(int((self.initial_width // 2) * 0.8)), height = 2)
        self.imported_image_folder_address_text_box.place(relx=relx_base, rely=rely_base * 3 + 0.1, anchor= "w")
        data_file_open_button = tk.Button(self.import_window, text="Browse", command = self.browse_directory_for_import)
        data_file_open_button.place(relx = relx_base * 4, rely = rely_base *3 + 0.1, anchor = "w")

        importFont = font.Font(size=20)
        import_button = tk.Button(self.import_window, text = "Import", fg='#0052cc', command = self.import_data)
        import_button["font"] = importFont
        import_button.place(relx = 0.5, rely = rely_base * 4, anchor = "w")

        self.import_window.mainloop()
    
    def import_data(self):
        image_folder_address = self.imported_image_folder_address_var.get()
        imported_project_name = self.imported_project_name_var.get()
        imported_project_data = eval(self.imported_data_var.get())
        if all([image_folder_address, imported_project_name, imported_project_data]):
            progress.import_progress_data(image_folder_address, imported_project_name, imported_project_data)
            self.import_window.quit()
            self.import_window.destroy()
        
        self.project_name = imported_project_name
        self.open_chosen_project()

    def create_export_results_window(self):
        response = messagebox.askokcancel("Export results", "You have completed the current project.\nExport the results?" )
        return response

    def create_save_progress_window(self, message):
        response = messagebox.askokcancel("Save progress", message + "\nMove on to the next?" )
        return response

    def create_open_window(self):
        self.open_window = Toplevel(self.root)
        self.open_window.title("Open")
        self.open_window.geometry(f"{self.initial_width // 2}x{self.initial_height // 2}")
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
        self.choose_project_window.geometry(f"{self.initial_width // 2}x{self.initial_height // 2}")

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
        # menu bar
        right_menu_bar = self.add_frame(self.button_frame_height, self.button_frame_width, 1, 0, 1, 1, self.root, "e")
        
        self.open_btn = self.add_button("Open", self.create_open_window, 2, 3, 0, 0, 1, 1, right_menu_bar, sticky = "e")
        self.import_btn = self.add_button("Import", self.create_import_window, 2, 3, 1, 0, 1, 1, right_menu_bar, sticky = "e")
        self.export_btn = self.add_button("Export", self.export, 2, 3, 2, 0, 1, 1, right_menu_bar, sticky = "e")
        self.save_btn = self.add_button("Save", self.save, 2, 3, 3, 0, 1, 1, right_menu_bar, sticky = "e")
        self.exit_btn = self.add_button("Exit", self.exit, 2, 3, 4, 0, 1, 1, right_menu_bar, sticky = "e")

        left_menu_bar = self.add_frame(self.button_frame_height, self.button_frame_width,0, 0, 1, 1, self.root, "we")
        # left_menu_bar.columnconfigure(1, weight=1)
        self.project_title_label = self.add_text("Project Title: ", 0, 0, 1, 1, left_menu_bar, sticky= "w")
        self.stage_label = self.add_text("Current Stage: ", 0, 1, 1, 1, left_menu_bar, sticky= "w")

        self.frame = self.add_frame(self.display_frame_height, self.display_frame_width, 0, 1, 2, 1, self.root)

    def create_pair_frame(self):
        self.frame.grid_forget()
        self.frame = self.add_frame(self.display_frame_height, self.display_frame_width, 0, 1, 2, 1, self.root)
        self.frame.rowconfigure(0, weight = 1)
        self.frame.columnconfigure(0, weight = 1)
        self.left_image = self.add_image(os.path.join("images","blank.png"), 0, 1, 1, 1, self.frame, "w", self.image_height_pixel, 0, 0)
        self.right_image = self.add_image(os.path.join("images","blank.png"), 1, 1, 2, 1, self.frame, "w", self.image_height_pixel, 0, 0)

        self.left_info_bar = self.add_frame(self.button_frame_height, self.button_frame_width,0, 2, 1, 1, self.frame)
        self.left_image_name_label = self.add_text("Name : ", 0, 0, 1, 1, self.left_info_bar, sticky= "w")
        self.left_cluster_label = self.add_text("Cluster : ", 0, 1, 1, 1, self.left_info_bar, sticky= "w")

        self.right_info_bar = self.add_frame(self.button_frame_height, self.button_frame_width // 2,1, 2, 1, 1, self.frame, "w")
        self.right_image_name_label = self.add_text("Name : ", 0, 0, 1, 1, self.right_info_bar, sticky="w")
        self.right_cluster_label = self.add_text("Cluster : ", 0, 1, 1, 1, self.right_info_bar, sticky="w")

        self.right_tick =self.add_image(os.path.join("images","blank.png"), 1, 0, 1, 1, self.right_info_bar, "w", 15, 0, 0)

        right_navigation_bar = self.add_frame(self.button_frame_height, self.button_frame_width //2,2, 2, 1, 1, self.frame, "e")
        #navigation buttons
        self.prev_btn = self.add_button("◀", self.pair_frame_load_prev_image, 4, 4, 0, 0, 1, 2, right_navigation_bar, sticky="e")
        self.next_btn = self.add_button("▶", self.pair_frame_load_next_image, 4, 4, 1, 0, 1, 2, right_navigation_bar, sticky="e")

        #action buttons
        action_bar = self.add_frame(self.button_frame_height, self.button_frame_width,1, 3, 2, 1, self.frame, "se")
        action_bar.rowconfigure(0, weight=1)
        for i in range(4):
            action_bar.columnconfigure(i, weight=1)

        action_button_height = 4

        self.no_match_btn = self.add_button("No Match (N)", self.pair_frame_mark_no_match, action_button_height, 12, 1, 0, 1, 1, action_bar, "se")
        self.match_btn = self.add_button("Match (M)", self.pair_frame_mark_match, action_button_height, 12, 2, 0, 1, 1, action_bar, "se")

    def start(self):
        self.create_UI()
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error("====Error in main loop====")
            logger.error(e.with_traceback)
            logger.error(f"progress_data{self.progress_data}")

#%% Methods for both Pair and Group display frame
    def _has_been_checked(self, image_name):
        return image_name in self.cluster.matches or image_name in self.cluster.nomatches

    def _mark_compared(self):
        right_image_name = self._get_image_name(self.right_image_index)
        self.cluster.compared_before.add(right_image_name)

    def _change_button_color (self, button_widget, new_fg = "black", new_font = ("Arial", "14")):
        button_widget.config (fg = new_fg, font = new_font)

    def _activate_button (self, button_widget):
        self._change_button_color (button_widget, new_fg = "#dda15e", new_font = ("Arial", "14", "bold"))

    def _deactivate_button (self, button_widget):
        self._change_button_color (button_widget, new_fg = "black", new_font = ("Arial", "14"))

# %% Actions for the Pair Display frame
    def pair_frame_update_cluster_label(self):
        right_cluster_label = self._get_image_object(self.right_image_index).cluster
        if len(right_cluster_label) > 40:
            right_cluster_label = right_cluster_label[:40] + "..."
        else:
            right_cluster_label = right_cluster_label + " " * (43 - len(right_cluster_label))
        self.right_cluster_label.config(text = "Cluster : " + right_cluster_label)

        left_cluster_label = self._get_image_object(self.left_image_index).cluster
        if len(left_cluster_label) > 40:
            left_cluster_label = left_cluster_label[:40] + "..."
        else:
            left_cluster_label = left_cluster_label + " " * (43 - len(left_cluster_label))
        self.left_cluster_label.config(text = "Cluster : " + left_cluster_label)

    def pair_frame_update_image_label(self):

        if self._get_image_object(self.right_image_index):
            right_image_label = self._get_image_object(self.right_image_index).name
        else:
            right_image_label = ""

        if len(right_image_label ) > 40:
            right_image_label  = right_image_label [:40] + "..."
        else:
            right_image_label = right_image_label + " " * (43 - len(right_image_label))
        self.right_image_name_label .config(text = "Name : " + right_image_label )

        left_image_label = self._get_image_object(self.left_image_index).name
        if len(left_image_label) > 40:
            left_image_label = left_image_label[:40] + "..."
        else:
            left_image_label = left_image_label + " " * (43 - len(left_image_label))
        self.left_image_name_label.config(text = "Name : " + left_image_label)

    def add_image(self,  path, column, row, columspan, rowspan, parent, sticky="nsew", max_height = None, padx = 0, pady = 0):

        image = Image.open(path)
        iw, ih = int(image.width), int(image.height)
        if not max_height:
            h = int(self.root.winfo_height() * 0.7)

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

    def pair_frame_refresh_image_display(self):
        """display left and right images"""

        best_image_index = self.cluster.get_best_image_index()
        if best_image_index == 0:
            self.left_image_index = 0
            self.right_image_index = 1
        else:
            self.left_image_index = best_image_index
            self.right_image_index = 0

        #skip the index of left image
        if self.right_image_index == self.left_image_index:
            self.right_image_index = min(len(self.cluster.images), self.right_image_index + 1)

        self.pair_frame_add_images(self.left_image_index, self.right_image_index)

        self.project_title_label.config(text = str("Project Title: " + self.project_name))
        self.stage_label.config(text = str("Current Stage: " + self.stage.name))

        #update image info display
        self.pair_frame_update_image_label()
        self.pair_frame_update_cluster_label()
        self.pair_frame_update_icon_button_color()

        self.prev_btn["state"] = "disabled"
        self.next_btn["state"] = "normal"

    def pair_frame_add_images (self, left_image_number, right_image_number):
        """Add left and right images at once. Assume self.left_image and self.right_image have been created prior.

        Args:
            left_image_number ([int]): index of image in self.cluster.images
            right_image_number ([int]): index of image in self.cluster.images

        Returns:
            None
        """
        left_path = self._get_image_address(left_image_number)
        left_img = self.create_image_object(left_path)
        right_path = self._get_image_address(right_image_number)
        right_img = self.create_image_object(right_path)

        self.left_image.configure(image = left_img)
        self.left_image.image = left_img
        self.right_image.configure(image = right_img)
        self.right_image.image = right_img

        #initialize tick and button style
        if self._has_been_checked(self._get_image_name(right_image_number)):
            self.pair_frame_change_tick_color("right", True)
        else:
            self.pair_frame_change_tick_color("right", False)

        if self._get_image_name(right_image_number) in self.cluster.matches:
            #the pair has been previously matched
            self._activate_button(self.match_btn)

        return None

    def pair_frame_change_tick_color (self, side, checked):
        """turn the "check" icon green or grey

        Args:
            tick_widget ([type]): [description]
            checked ([bool]): whether the image has been checked
        """
        if checked:
            tick_img = self.create_image_object(os.path.join("images","green_tick.png"),15)
        else:
            tick_img = self.create_image_object(os.path.join("images","grey_tick.png"),15)

        self.right_tick.configure(image = tick_img)
        self.right_tick.image = tick_img

    def pair_frame_update_icon_button_color (self):
        """When browsing through images, update icon and button styles based on what action has been done to the right image
        """

        #the pair has been previously matched
        if self._get_image_name(self.right_image_index) in self.cluster.matches:
            self._activate_button(self.match_btn)
            self.pair_frame_change_tick_color("right", True)

        else:
            self._deactivate_button(self.match_btn)
            self.pair_frame_change_tick_color("right", False)

        #if the pair has been unmatched:
        if self._get_image_name(self.right_image_index) in self.cluster.nomatches:
            self._activate_button(self.no_match_btn)
            self.pair_frame_change_tick_color("right", True)
        else:
            self._deactivate_button(self.no_match_btn)


    def pair_frame_load_next_image (self):
        """Change right image. Erase old image, Add the next in line image. function for "next" button

        """
        self.right_image_index = min(len(self.cluster.images), self.right_image_index + 1)
        if self.right_image_index < len(self.cluster.images):
            new_image_path = self._get_image_address(self.right_image_index)
            new_img = self.create_image_object(new_image_path)
            self.right_image.configure(image = new_img)
            self.right_image.image = new_img
            self.pair_frame_update_cluster_label()
            self.pair_frame_update_icon_button_color ()
            self.next_btn["state"] = "normal"
        else:
            new_image_path = os.path.join("images", "end.png")
            new_img = self.create_image_object(new_image_path)
            self.right_image.configure(image = new_img)
            self.right_image.image = new_img
            new_cluster_label = ""
            self.pair_frame_change_tick_color("right", False)
            self._deactivate_button(self.match_btn)
            self._deactivate_button(self.no_match_btn)
            self.right_cluster_label.config(text = "Cluster: " + new_cluster_label)
            self.next_btn["state"] = "disabled"
        
        if self.right_image_index > 1:
            self.prev_btn["state"] = "normal"
        else:
            self.prev_btn["state"] = "disabled"
        
        #update image labels
        self.pair_frame_update_image_label()
        #check for completion at the last image
        if self.right_image_index == len(self.cluster.images):
            self.pair_frame_check_completion_and_move_on()
        return None

    def pair_frame_load_prev_image (self):
        """ change right image
        When user reach the index 1 image, can't move forward anymore

        """
        curr_right_image_index = self.right_image_index
        self.right_image_index = max(0, self.right_image_index - 1)
        if self.right_image_index == 0 and \
                self.right_image_index == self.left_image_index:
            self.right_image_index = curr_right_image_index

        if self.right_image_index >= 0:
            new_image_path = self._get_image_address(self.right_image_index)
            new_img = self.create_image_object(new_image_path)
            self.right_image.configure(image = new_img)
            self.right_image.image = new_img
            self.pair_frame_update_image_label()
            self.pair_frame_update_cluster_label()
            self.pair_frame_update_icon_button_color ()

        if self.right_image_index > 1:
            self.prev_btn["state"] = "normal"
        else:
            self.prev_btn["state"] = "disabled"

        if self.right_image_index < len(self.cluster.images):
            self.next_btn["state"] = "normal"
        else:
            self.next_btn["state"] = "disabled"
        return None

    def pair_frame_mark_match (self):
        """During cluster validation stage, match left and right image
        - the right tick turn green (means checked)
        - the match button's fg turn orange
        - the right image object added to cluster.matchs
        - take object out from cluster.nomatches if init

        """
        if self.right_image_index < len(self.cluster.images):
            self.pair_frame_change_tick_color ("right", checked = True)
            self._activate_button(self.match_btn)
            self._deactivate_button(self.no_match_btn)

            #add to match
            self.cluster.matches.add(self._get_image_name(self.right_image_index))
            #delist from nomatches
            if self._get_image_name(self.right_image_index) in self.cluster.nomatches:
                self.cluster.nomatches.remove(self._get_image_name(self.right_image_index))
                
            self._mark_compared()
            logger.info("Match {} to cluster {}".format(self._get_image_name(self.right_image_index),self.cluster.name))

        if self.testing_mode:
            self.test.record_action(self._get_image_name(self.left_image_index), self._get_image_name(self.right_image_index), "match")

    def pair_frame_mark_no_match (self):
        """During cluster validation stage, unmatch left and right image
        - the right tick turn green (means checked)
        - the unmatch button's fg turn orange
        - the right image object added to cluster.unmatchs
        - remove right from cluster.matches
        - update right_cluster_label to "Singles"
        - update the image's cluster to singles

        """
        if self.right_image_index < len(self.cluster.images):
            self.pair_frame_change_tick_color ("right", checked = True)
            self._activate_button(self.no_match_btn)
            self._deactivate_button(self.match_btn)

            #add to nomatch
            self.cluster.nomatches.add(self._get_image_name(self.right_image_index))
            #delist from matches
            if self._get_image_name(self.right_image_index) in self.cluster.matches:
                self.cluster.matches.remove(self._get_image_name(self.right_image_index))
                
            self._mark_compared()
            logger.info("Unmatch {} from cluster {}".format(self._get_image_name(self.right_image_index), self.cluster.name))
        if self.testing_mode:
            self.test.record_action(self._get_image_name(self.left_image_index), self._get_image_name(self.right_image_index), "unmatch")

    def pair_frame_check_completion_and_move_on (self):
        """This function is called when user clicks "next" while at the last image
        !!! only mark cluster complete if user clicks ok"""

        if progress.check_cluster_completion(self.cluster,self.stage):
            self.stage = progress.mark_cluster_completed(self.cluster, self.stage, self.progress_data[self.project_name]["clusters"])
            completion_status = "cluster"
            if self.testing_mode:
                self.test.translate_actions(self.stage.stage_number)
        else:
            return None

        if progress.check_part1_completion(self.cluster, self.stage, self.progress_data[self.project_name]["clusters"]):
            logger.info(f"_____STAGE {self.stage.name} COMPLETED_____")
            logger.debug(f"Part 1 completed")
            logger.info(str(self.progress_data))
            completion_status = "part1"
            message = "You have completed the current *STAGE*."
            response = self.create_save_progress_window(message)
            if response:
                self.progress_data, self.stage = progress.update_progress_data(self.project_name, self.stage,self.cluster,self.progress_data)
                self.cluster, self.stage = progress.create_new_objects(self.cluster, self.stage, self.project_name, self.progress_data, completion_status)
                if self.testing_mode:
                    self.test.test_cluster_correctedness(self.progress_data[self.project_name]["clusters"])
                    self.test.test_comparison(self.project_name, self.stage.stage_number, self.progress_data[self.project_name]["clusters"])
                    self.test.test_image_number(self.progress_data[self.project_name]["clusters"],self.project_name)
                self.group_frame_start(identical_stage= True)
                return None
            else:
                self.stage = progress.unmark_cluster_completed(self.cluster, self.stage, self.progress_data[self.project_name]["clusters"])
        else:
            if progress.check_stage_completion(self.stage, self.progress_data[self.project_name]["clusters"]):
                message = "You have completed the current *STAGE*."
                completion_status = "stage"
                logger.info("_____STAGE {} COMPLETED_____".format(self.stage.name))
                logger.info(f"{self.progress_data}")
                if self.testing_mode:
                    self.test.test_comparison(self.project_name, self.stage.stage_number, self.progress_data[self.project_name]["clusters"])
                    self.test.clear_comparisons()
            elif completion_status == "cluster":
                message = "You have completed the current cluster."
            else:
                return None
            response = self.create_save_progress_window(message)
            if response:
                self.progress_data, self.stage = progress.update_progress_data(self.project_name, self.stage,self.cluster,self.progress_data)
                self.cluster, self.stage= progress.create_new_objects(self.cluster, self.stage, self.project_name, self.progress_data, completion_status)
                if self.testing_mode:
                    self.test.test_cluster_correctedness(self.progress_data[self.project_name]["clusters"])

                #update display
                if self.stage.stage_number == 3:
                    self.group_frame_start(identical_stage = True)
                else:
                    self.pair_frame_refresh_image_display()
            else:
                self.stage = progress.unmark_cluster_completed(self.cluster, self.stage, self.progress_data[self.project_name]["clusters"])
                #todo update test
        self.root.after(1, lambda: self.root.focus_force())

    def pair_frame_bind_keys(self):
        self.root.bind('<Right>', lambda event: self.pair_frame_load_next_image())
        self.root.bind('<Left>', lambda event: self.pair_frame_load_prev_image())
        self.root.bind('m', lambda event: self.pair_frame_mark_match())
        self.root.bind('n', lambda event: self.pair_frame_mark_no_match())
    
    def pair_frame_start(self): 
        self.frame.grid_forget()
        self.create_pair_frame()
        self.pair_frame_bind_keys()
        self.pair_frame_refresh_image_display()
        self.root.after(1, lambda: self.root.focus_force())

#%% Actions for the Group Display Frame
    #functionality
    def group_frame_add_image_to_list (self, image_object):
        """add the image associated with the "add" button to the identical list
        function triggered by pressing "add" button.
        """
        if not image_object:
            return None
        if image_object.name in self.added_coin_dict:
            return None
        if image_object.name in self.marked_added_coin_dict:
            return None
        self.added_coin_dict[image_object.name] = image_object
        self.added_coin_list_box.insert(tk.END, image_object.name)
        #display current image in the small window if it's the first on the list
        if len(self.added_coin_dict) == 1:
            img = self.create_image_object(os.path.join(self.project_address, image_object.name), int(self.right_main_frame_width_pixel * 0.7))
            self.right_image_window.configure(image = img)
            self.right_image_window.image = img
            if self.stage.stage_number == 0:
                self.added_coin_list_box.itemconfig(0,{'bg':'khaki3'})

        self.added_coin_list_box.select_anchor(tk.END) 

    def _add_function_0(self):
        image_object = self.image_on_display[0][0]
        self.group_frame_add_image_to_list(image_object)

    def _add_function_1(self):
        image_object = self.image_on_display[1][0]
        self.group_frame_add_image_to_list(image_object)

    def _add_function_2(self):
        image_object = self.image_on_display[2][0]
        self.group_frame_add_image_to_list(image_object)

    def _add_function_3(self):
        image_object = self.image_on_display[3][0]
        self.group_frame_add_image_to_list(image_object)

    def _add_function_4(self):
        image_object = self.image_on_display[4][0]
        self.group_frame_add_image_to_list(image_object)

    def _add_function_5(self):
        image_object = self.image_on_display[5][0]
        self.group_frame_add_image_to_list(image_object)

    def _add_function_n(self,n):
        if n == 0:
            return self._add_function_0
        elif n == 1:
            return self._add_function_1
        elif n == 2:
            return self._add_function_2
        elif n == 3:
            return self._add_function_3
        elif n == 4:
            return self._add_function_4
        elif n == 5:
            return self._add_function_5

    def group_frame_remove_image_from_list (self):
        """Remove a selected item from the identical list.
        If the removed coin is the first one on the list. The second one will be displayed.
        If the removed coin is the only one on the list. The display window will be blank.
        """
        image_name = self.added_coin_list_box.get(tk.ANCHOR)
        if not image_name in self.added_coin_dict:
            return None
        self.added_coin_dict.pop(image_name)
        self.added_coin_list_box.delete(tk.ANCHOR)

        if len(self.added_coin_dict) > 0 :
            default_image_name = self.added_coin_list_box.get(0)
            default_image_object = self.added_coin_dict[default_image_name]
            img = self.create_image_object(os.path.join(self.project_address, default_image_object.name), int(self.right_main_frame_width_pixel * 0.7))
        else:
            img = self.create_image_object(os.path.join("images","blank.png"), int(self.right_main_frame_width_pixel * 0.7))
        self.right_image_window.configure(image = img)
        self.right_image_window.image = img

    def group_frame_mark_best_image(self):

        if self.stage.stage_number == 3:
            return None
        
        image_name = self.added_coin_list_box.get(tk.ANCHOR)
        if image_name == self.added_coin_list_box.get(0):
            return None

        if not image_name in self.added_coin_dict:
            return None

        #de-highlight old best image (first image)
        self.added_coin_list_box.itemconfig(0,{'bg':'white'})

        #move selected item to the top of the list
        self.added_coin_list_box.delete(tk.ANCHOR)
        self.added_coin_list_box.insert(0, image_name)

        #highlight the item
        self.added_coin_list_box.itemconfig(0,{'bg':'khaki3'})

        #update preview window
        img = self.create_image_object(os.path.join(self.project_address, image_name), int(self.right_main_frame_width_pixel * 0.7))
        self.right_image_window.configure(image = img)
        self.right_image_window.image = img

        logger.info("Make {} best image for the cluster".format(image_name))

    def group_frame_onselect(self, evt):
        """update the display window according to the image being selected

        Args:
            evt ([tkinter event]): a tkinter event
        """
        w = evt.widget
        index = int(w.curselection()[0])
        image_name = w.get(index)
        image_object = self.added_coin_dict[image_name]
        img = self.create_image_object(os.path.join(self.project_address, image_object.name), int(self.right_main_frame_width_pixel * 0.7))
        self.right_image_window.configure(image = img)
        self.right_image_window.image = img


    def group_frame_confirm_current_list (self):
        """mark the images on the list matches and un-display their widgets.
        reset the identical list and display window.
        """
        if len(self.added_coin_dict) <= 1:
            return None

        logger.info(f"Confirm coin list {self.added_coin_dict.keys()}")
        self.marked_added_coin_dict.update(self.added_coin_dict)
        added_coin_list = list(self.added_coin_dict.keys())
        best_image_name = self.added_coin_list_box.get(0)
        self.marked_coin_group_list.append((added_coin_list, best_image_name))

        self.group_frame_reset_identical_list_box()

    def group_frame_reset_identical_list_box(self):
        #reset list
        self.added_coin_list_box.delete(0,tk.END)
        self.added_coin_dict = {}

        #reset right window
        img = self.create_image_object(os.path.join("images", "blank.png"), int(self.right_main_frame_width_pixel * 0.7))
        self.right_image_window.configure(image = img)
        self.right_image_window.image = img
        #reset left window
        self.group_frame_refresh_image_display()

    def group_frame_finish_project(self):
        logger.info("_____PROJECT COMPLETED_____")
        logger.info(str(self.progress_data))
        exported = self.export(project_completed= True)
        return exported

    def group_frame_check_completion_and_move_on(self):
        """This function is called when user clicks "next" while at the last image
        !!! only mark cluster complete if user clicks ok"""

        #user confirms that the cluster is completed
        self.stage = progress.mark_cluster_completed(self.cluster, self.stage, self.progress_data[self.project_name]["clusters"])
        completion_status = "cluster"
        if self.testing_mode and self.stage.stage_number == 0:
            self.test.update_test_data_stage0(self.marked_coin_group_list, set(self.cluster.images_dict.keys()))
        if progress.check_project_completion(self.stage, self.progress_data[self.project_name]["clusters"]):
            if self.testing_mode:
                self.test.test_image_number(self.progress_data[self.project_name]["clusters"], self.project_address)
            exported = self.group_frame_finish_project()
            if not exported:
                self.stage = progress.unmark_cluster_completed(self.cluster, self.stage, self.progress_data[self.project_name]["clusters"])
        else:
            if progress.check_stage_completion(self.stage, self.progress_data[self.project_name]["clusters"]):
                message = "You have completed the current *STAGE*."
                completion_status = "stage"
                logger.info(f"_____STAGE {self.stage.name} COMPLETED_____")
                logger.info(f"{self.progress_data}")
                if self.testing_mode:
                    self.test.test_comparison(self.project_name, self.stage.stage_number,self.progress_data[self.project_name]["clusters"])
                    self.test.clear_comparisons()
            elif completion_status == "cluster":
                message = "You have completed the current cluster."
            else:
                return None
            response = self.create_save_progress_window(message)
            if response:
                self.progress_data, self.stage = progress.update_progress_data(self.project_name, self.stage,self.cluster,self.progress_data, self.marked_coin_group_list)
                self.cluster, self.stage= progress.create_new_objects(self.cluster, self.stage, self.project_name, self.progress_data, completion_status)
                if self.testing_mode:
                    self.test.test_cluster_correctedness(self.progress_data[self.project_name]["clusters"])

                #update display
                if self.stage.stage_number == 1 or self.stage.stage_number == 2:
                    self.pair_frame_start()
                else:
                    self.group_frame_refresh_image_display()
               
            else:
                self.stage = progress.unmark_cluster_completed(self.cluster, self.stage, self.progress_data[self.project_name]["clusters"])
                #todo update test
        self.root.after(1, lambda: self.root.focus_force())

    def group_frame_next_cluster(self):
        """Save current progress and display next cluster
        If all clusters have been visited -> end of project
        """
        if len(self.added_coin_dict) > 1:
            confirm_list = messagebox.askyesno("Next Cluster", "Confirm current list of coins?")
            if confirm_list:
                self.group_frame_confirm_current_list()
            else:
                self.group_frame_reset_identical_list_box()
        else:
            self.group_frame_reset_identical_list_box()

        if self.stage.stage_number == 3:
            for group, _ in self.marked_coin_group_list:
                self.cluster.identicals.append(set(group))

        self.group_frame_check_completion_and_move_on()
        if not self.quit:
            self.current_page = 0
            self.group_frame_refresh_image_display()
            self.initialize_stack()
            self.root.after(1, lambda: self.root.focus_force())

    def group_frame_load_next_page(self) -> None:
        self.current_page = min(self.current_page + 1, math.ceil(len(self.cluster.images)/6 ) - 1)
        self.group_frame_refresh_image_display()

    def group_frame_load_prev_page(self) -> None:
        self.current_page = max(self.current_page - 1, 0)
        self.group_frame_refresh_image_display()

    #visuals
    def group_frame_refresh_image_display(self) -> None:
        """show current cluster's coin images. Add the image widgets to the image_widgets dictionary"""
        self.project_title_label.config(text = str("Project Title: " + self.project_name))
        self.stage_label.config(text = str("Current Stage: " + self.stage.name))
        self.main_frame_height = int(self.root.winfo_height() * 0.8)
        cluster_label = self.cluster.name
        if len(cluster_label) > 40:
            cluster_label = cluster_label[:40] + "..."
        self.current_cluster_label.config(text = f"Current Cluster: " + cluster_label)

        for i in range(self.current_page*6, (self.current_page + 1)*6):
            display_index = i % 6
            self.image_label_widgets[display_index].config(text = "")

            if i >= len(self.cluster.images):
                path = "images/blank.png"
                img = self.create_image_object(path, int(self.main_frame_height * 0.49))
                image_object = None
            else:
                image_object = self._get_image_object(i)
                self.image_label_widgets[display_index].config(text = image_object.name)
                if image_object.name in self.marked_added_coin_dict:
                    img = self.create_darken_image_object(self._get_image_address(i), int(self.main_frame_height * 0.49))
                else:
                    img = self.create_image_object(self._get_image_address(i),int(self.main_frame_height * 0.49))
            self.image_on_display[display_index][1].configure(image = img )
            self.image_on_display[display_index][1].image = img
            image_widget = self.image_on_display[display_index][1]
            self.image_on_display[display_index]= (image_object, image_widget)
        
        #disable next page button if there's not more next pages (aka last index displayed is the last index in cluster.images)
        if (self.current_page + 1)*6 >= len(self.cluster.images) :
            self.next_btn["state"] = "disabled"
        else:
            self.next_btn["state"] = "normal"
        
        #disable prev page button if there's no more prev pages
        if self.current_page == 0:
            self.prev_btn["state"] = "disabled"
        else:
            self.prev_btn["state"] = "normal"

    def initialize_stack(self):
        # a dictionary of image objects currently on the stack. Key: image name. Value: image object
        self.added_coin_dict = {}
        #keep track of coins that have been confirmed Key: image name. Value: image object
        self.marked_added_coin_dict = {}
        #keep track of identified groups (list of list of tuples)
        self.marked_coin_group_list = [] #([name1, name2, name3], best_image_name)

    def create_group_frame (self, identical_stage = False):
        #the first 6 images will be on page 0, the next 6 on page 1 etc.
        self.current_page = 0
        self.frame.grid_forget()
        self.frame = self.add_frame(self.display_frame_height, self.display_frame_width, 0, 1, 2, 1, self.root)
        # menu bar
        self.left_main_frame_width_pixel = int(self.initial_width * 0.68)
        self.right_main_frame_width_pixel = int(self.initial_width * 0.28)
        self.main_frame_height = int(self.root.winfo_height() * 0.8)

        #left main frame: display coin images Height: 0.8 * window, width: 0.7 * window width
        self.left_main_frame = self.add_frame(self.main_frame_height, self.left_main_frame_width_pixel, 0, 1, 1, 2, self.frame, "nw")
        #right main frame: display current identical groups
        self.right_main_frame = self.add_frame(self.main_frame_height, self.right_main_frame_width_pixel, 1, 1, 1, 2, self.frame, "ne")

        self.initialize_stack()

        #identical coin list box displays the names of the identical coins
        self.scrollbar = tk.Scrollbar(self.right_main_frame, orient = tk.VERTICAL)
        self.added_coin_list_box = tk.Listbox(self.right_main_frame, 
                                            height = self._pixel_to_char(int(self.main_frame_height * 0.1)),
                                            width = self._pixel_to_char(int(self.right_main_frame_width_pixel * 0.8)),
                                            yscrollcommand= self.scrollbar.set)

        self.scrollbar.config(command = self.added_coin_list_box.yview)
        self.scrollbar.grid(column = 1, row = 2, sticky = "ns")

        self.added_coin_list_box.grid(column = 0, row = 2, columnspan= 1, rowspan= 1, sticky = "we" )

        self.added_coin_list_box.bind('<<ListboxSelect>>', self.group_frame_onselect)

        #Left main frame can display max 6 pictures.
        self.image_on_display = {} #key: element index (0-5), value: (image object, image widget)
        self.image_label_widgets = []
        self.image_frames = []

        for i in range(6):
            col = i % 3
            row = i // 3
            image_frame = self.add_frame(int(self.main_frame_height * 0.45),int(self.main_frame_height * 0.45), col, row, 1, 1, self.left_main_frame, "nsew")
            self.image_frames.append(image_frame)
            image_filler = self.add_image("images/blank.png", 0, 0, 2, 1, image_frame, "n", int(self.main_frame_height * 0.45))
            self.image_on_display[i] = (None, image_filler)
            image_label = self.add_text("", 0,1,1,1, image_frame, "se")
            add_function = self._add_function_n(i)
            _ = self.add_button(f"Add ({i + 1})", add_function , self._pixel_to_char(int(self.main_frame_height * 0.01)), 5, 1,1,1,1, image_frame, "se")
            self.image_label_widgets.append(image_label)

        #a small image for easy comparison
        self.right_image_window = self.add_image("images/blank.png", 0,0,1,1,self.right_main_frame, "we", int(self.right_main_frame_width_pixel * 0.7))
        
        if identical_stage:
            image_list_label = "Add images of identical coins: "
        else:
            image_list_label = "Add images of matched coins: "
        _ = self.add_text(image_list_label, 0, 1, 1, 1, self.right_main_frame, "w")

        #buttons
        list_button_frame = self.add_frame(5,self.right_main_frame_width_pixel * 0.8, 0, 3,2,1,self.right_main_frame, "w")
        _ = self.add_button("Remove from list (R)", self.group_frame_remove_image_from_list, 2, 17, 0, 3, 1,1, list_button_frame, "w")
        best_image_btn = self.add_button("Mark best image (B)", self.group_frame_mark_best_image, 2, 17, 1, 3, 1,1, list_button_frame, "e")
        if identical_stage:
            best_image_btn["state"] = "disabled"
        _ = self.add_button("Confirm current list (C)", self.group_frame_confirm_current_list, 2,17, 0, 4, 1,1, list_button_frame, "w")

        prev_next_frame = self.add_frame(5,self.right_main_frame_width_pixel * 0.8, 0, 4, 2,1,self.right_main_frame, "w")
        self.prev_btn = self.add_button("◀", self.group_frame_load_prev_page, 4, 4, 0, 0, 1, 1, prev_next_frame , sticky="sw")
        self.next_btn= self.add_button("▶", self.group_frame_load_next_page, 4, 4, 1, 0, 1, 1, prev_next_frame , sticky="sw")

        _ = self.add_button("Next Cluster (N)", self.group_frame_next_cluster, 3, 19, 1, 2, 1, 1, self.frame, "sw" )
        self.current_cluster_label  = self.add_text("Current cluster: ",0, 3, 1, 1, self.frame, "w" )

    def group_frame_start(self, identical_stage = False):
        self.frame.grid_forget()
        self.create_group_frame(identical_stage)
        self.group_frame_refresh_image_display()
        self.root.bind('<Right>', lambda event: self.group_frame_load_next_page())
        self.root.bind('<Left>', lambda event: self.group_frame_load_prev_page())
        self.root.bind('c', lambda event: self.group_frame_confirm_current_list())
        self.root.bind('r', lambda event: self.group_frame_remove_image_from_list())
        self.root.bind('b', lambda event: self.group_frame_mark_best_image())
        self.root.bind('n', lambda event: self.group_frame_next_cluster())
        self.root.bind('1', lambda event: self._add_function_0())
        self.root.bind('2', lambda event: self._add_function_1())
        self.root.bind('3', lambda event: self._add_function_2())
        self.root.bind('4', lambda event: self._add_function_3())
        self.root.bind('5', lambda event: self._add_function_4())
        self.root.bind('6', lambda event: self._add_function_5())
        self.root.after(1, lambda: self.root.focus_force())

# %%

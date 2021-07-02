import tkinter as tk
from tkinter.constants import RAISED, RIDGE
from PIL import Image, ImageTk
import math
import actions
from tkinter import filedialog
from tkinter.filedialog import askopenfile
import os
from objects import *
import actions


class MainUI:
    def __init__(self):
        # main interface
        self.root = tk.Tk()
        self.root.title("Die Study Tool")
        self.project_name = ""
        self.project_address = ""
        self.root.geometry("1300x850")
        self.root.minsize(width=1300, height=850)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)

#%% Shortcuts

    def _get_image_object(self, image_index):
        if image_index < len(self.cluster.images):
            return self.cluster.images [image_index]

    def _get_image_name (self, image_index):
        if image_index < len(self.cluster.images):
            return self._get_image_object(image_index).name

    def _add_to_identicals (self, left_image_obj, right_image_obj):
        found = False
        for s in self.cluster.identicals:
            if left_image_obj in s:
                s.add(right_image_obj)
                found = True

        if not found:
            self.cluster.identicals.append(set([left_image_obj, right_image_obj]))

    def _remove_from_identicals (self, left_image_obj, right_image_obj):
        for s in self.cluster.identicals:
            if left_image_obj in s:
                s.remove(right_image_obj)

    def _is_identical(self, left_image_obj, right_image_obj):
        for s in self.cluster.identicals:
            if left_image_obj in s and right_image_obj in s:
                return True
        return False
#%% Visuals and Aesthetics

    def add_image(self,  path, column, row, columspan, rowspan, parent, sticky="nsew"):

        image = Image.open(path)
        iw, ih = int(image.width), int(image.height)
        h = 600
        image = image.resize((math.ceil(h/ih * iw), h), Image. ANTIALIAS)
        img = ImageTk.PhotoImage(image)
        img_label = tk.Label(parent, image=img)
        img_label.image = img
        img_label.grid(column=column,
                       row=row,
                       columnspan=columspan,
                       rowspan=rowspan,
                       sticky=sticky)
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

    def add_frame(self, column, row, columspan, rowspan, parent, sticky="nsew"):
        frame = tk.Frame(parent, padx=6, pady=6, bd=0, width = 640, height = 80, bg = "white")
        frame.grid(column=column,
                   row=row,
                   columnspan=columspan,
                   rowspan=rowspan,
                   sticky=sticky)

        return frame

    def add_filler(self, height, width, column, row, columspan, rowspan, parent, sticky="nsew", content = ""):
        filler = tk.Label(parent, width=width, height=height, text = content, bg = "red")
        filler.grid(column=column,
                    row=row,
                    columnspan=columspan,
                    rowspan=rowspan,
                    sticky=sticky)

        return filler


    def add_images (self, left_image_number, right_image_number):
        """Add left and right images at once

        Args:
            left_image_number ([type]): index of image in self.cluster.images
            right_image_number ([type]): index of image in self.cluster.images

        Returns:
            TK Widget: left and right image widgets
        """
        left_path = self.cluster.images[left_image_number].address
        left_image = self.add_image(left_path, 0, 1, 1, 1, self.root, sticky = "we")
        # self.add_filler(1, 1, 1, 0, 1, 4, self.root, sticky = "w") #divider
        right_path = self.cluster.images[right_image_number].address
        right_image = self.add_image(right_path, 2, 1, 1, 1, self.root, sticky = "we")

        #initialize tick and button style
        if self._get_image_name(right_image_number) in self.current_stage.images_checked:
            self.change_tick_color("right", True)
        else:
            self.change_tick_color("right", False)

        if self._get_image_object(right_image_number) in self.cluster.matches:
            #the pair has been previously matched
            self.activate_button(self.match_btn)

        return left_image, right_image

    def change_tick_color (self, side, checked):
        """turn the "check" icon green or grey

        Args:
            tick_widget ([type]): [description]
            checked ([type]): [description]
        """
        if side == "left":
            tick_widget = self.left_tick
            frame_widget = self.left_info_bar

        else:
            tick_widget = self.right_tick
            frame_widget = self.right_info_bar

        tick_widget.grid_forget()
        if checked:
            tick_widget = self.add_icon("images/green_tick.png", 15, 15, 1, 0, 1, 1, frame_widget, sticky = "e")

        else:
            tick_widget = self.add_icon("images/grey_tick.png", 15, 15, 1, 0, 1, 1, frame_widget, sticky = "e")


    def update_icon_button_color (self):
        """When browsing through images, update icon and button styles based on what action has been done to the right image
        """
        #update tick color
        if self._get_image_name(self.right_image_index) in self.current_stage.images_checked:
            self.change_tick_color("right", True)
        else:
            self.change_tick_color("right", False)
        #the pair has been previously matched
        if self._get_image_object(self.right_image_index) in self.cluster.matches:
            self.activate_button(self.match_btn)
        else:
            self.deactivate_button(self.match_btn)
        #if the pair has been unmatched:
        if self._get_image_object(self.right_image_index) in self.cluster.nomatches:
            self.activate_button(self.no_match_btn)
        else:
            self.deactivate_button(self.no_match_btn)
        #if the pair are identicals:
        if self._is_identical(self._get_image_object(self.left_image_index), self._get_image_object(self.right_image_index)):
            self.activate_button(self.identical_btn)
        else:
            self.deactivate_button(self.identical_btn)

    def change_button_color (self, button_widget, new_fg = "white", new_font = ("Arial", "14")):
        button_widget.config (fg = new_fg, font = new_font)

    def activate_button (self, button_widget):
        self.change_button_color (button_widget, new_fg = "#dda15e", new_font = ("Arial", "14", "bold"))

    def deactivate_button (self, button_widget):
        self.change_button_color (button_widget, new_fg = "white", new_font = ("Arial", "14"))

#%% Actions

    def browse_files(self):
        """Let user choose which project/folder to work on
        pass the directory name to the class
        open undone clusters
        show images
        """
        dirname = filedialog.askdirectory(parent=self.root)
        self.project_name = dirname.split("/")[-1]
        #update project name in menu bar
        self.project_title_label.config(text = "Project Title: " + self.project_name)

        #TODO: read progress
        #update project status

        self.current_stage = Stage(0)
        self.current_stage_label.config (text = "Current Stage: " + self.current_stage.name)

        self.project_address = dirname
        self.cluster = actions.open_cluster(project_address = self.project_address)

        #read or make Singles folder
        if not os.path.exists(dirname + "/" + "Singles"):
            os.mkdir(dirname + "/" + "Singles")
        self.singles = Cluster( str(dirname + "/" + "Singles"))

        self.left_image.grid_forget()
        self.right_image.grid_forget()

        #TODO: change staring index according to progress?

        self.left_image_index = 0
        self.right_image_index = 1
        self.left_image, self.right_image = self.add_images(self.left_image_index, self.right_image_index)

        #update image info display
        self.left_image_name_label.config(text = "Name : " + self.cluster.images[self.left_image_index].name)
        self.left_cluster_label.config(text = "Cluster : " + self.cluster.images[self.left_image_index].cluster)

        self.right_image_name_label.config(text = "Name : " + self.cluster.images[self.right_image_index].name)
        self.right_cluster_label.config(text = "Cluster : " + self.cluster.images[self.right_image_index].cluster)

        return None

    def load_next_image (self):
        """Change right image. Erase old image, Add the next in line image. function for "next" button

        """
        #skip the index of left image
        self.right_image_index = min(len(self.cluster.images), self.right_image_index + 1)
        if self.right_image_index == self.left_image_index:
            self.right_image_index = min(len(self.cluster.images), self.right_image_index + 1)

        self.right_image.grid_forget()

        if self.right_image_index < len(self.cluster.images):
            new_image_path = self.cluster.images[self.right_image_index].address
            self.right_image = self.add_image(new_image_path, 2, 1, 1, 1, self.root, sticky = "we")
            new_image_label =  self.cluster.images[self.right_image_index].name
            new_cluster_label = self.cluster.images[self.right_image_index].cluster
            self.update_icon_button_color ()

        else:
            self.add_filler(30,30, 2, 1, 1, 1, self.root, content = "End of Cluster")
            new_image_label =  ""
            new_cluster_label = self.cluster.name
            self.change_tick_color("right", False)
            self.deactivate_button(self.match_btn)
            self.deactivate_button(self.no_match_btn)
            self.deactivate_button(self.identical_btn)

        #update image labels
        self.right_image_name_label.config(text = "Name : " + new_image_label)
        self.right_cluster_label.config(text = "Cluster : " + new_cluster_label)

        return None

    def load_prev_image (self):
        """ change right image
        When user reach the index 1 image, can't move forward anymore

        """
        #skip the index of left image
        self.right_image_index = max(0, self.right_image_index - 1)
        if self.right_image_index == self.left_image_index:
            self.right_image_index = max(0, self.right_image_index - 1)

        if self.right_image_index == self.left_image_index and self.left_image_index == 0:
            self.right_image_index = 1

        self.right_image.grid_forget()
        if self.right_image_index >= 0:
            new_image_path = self.cluster.images[self.right_image_index].address
            self.right_image = self.add_image(new_image_path, 2, 1, 1, 1, self.root, sticky = "we")
            self.right_image_name_label.config(text = "Name : " + self.cluster.images[self.right_image_index].name)
            self.right_cluster_label.config(text = "Cluster : " +self.cluster.images[self.right_image_index].cluster)
            self.update_icon_button_color ()

        return None


    def cluster_validation_match (self):
        """During cluster validation stage, match left and right image
        - the right tick turn green (means checked)
        - the match button's fg turn orange
        - the right image object added to cluster.matchs
        - take object out from cluster.nomatches if init

        """
        if self.right_image_index < len(self.cluster.images):
            if self._get_image_name(self.right_image_index) not in self.current_stage.images_checked:
                self.change_tick_color ("right", checked = True)
                self.current_stage.images_checked.add(self._get_image_name(self.right_image_index))

            self.activate_button(self.match_btn)
            self.cluster.matches.add(self._get_image_object(self.right_image_index))
            #delist from nomatches
            if self._get_image_object(self.right_image_index) in self.cluster.nomatches:
                self.cluster.nomatches.remove(self._get_image_object(self.right_image_index))
                self.deactivate_button(self.no_match_btn)
                #delist from Singles
                self._get_image_object(self.right_image_index).cluster = self.cluster.name
                self.singles.images.remove(self._get_image_object(self.right_image_index))
                #update cluster label
                self.right_cluster_label.config(text = "Cluster :" + self.cluster.name)

    def cluster_validation_no_match (self):
        """During cluster validation stage, unmatch left and right image
        - the right tick turn green (means checked)
        - the unmatch button's fg turn orange
        - the right image object added to cluster.unmatchs
        - remove right from cluster.matches
        - add right to Singles cluster
        - update right_cluster_label to "Singles"
        - update the image's cluster to singles

        """
        if self.right_image_index < len(self.cluster.images):

            if self._get_image_name(self.right_image_index) not in self.current_stage.images_checked:
                self.change_tick_color ("right", checked = True)
                self.current_stage.images_checked.add(self._get_image_name(self.right_image_index))

            self.activate_button(self.no_match_btn)
            self.cluster.nomatches.add(self._get_image_object(self.right_image_index))
            #delist from matches
            if self._get_image_object(self.right_image_index) in self.cluster.matches:
                self.cluster.matches.remove(self._get_image_object(self.right_image_index))
                self.deactivate_button(self.match_btn)
            #delist from identicals
            if self._is_identical(self._get_image_object(self.left_image_index), self._get_image_object(self.right_image_index)):
                self._remove_from_identicals (self._get_image_object(self.left_image_index), self._get_image_object(self.right_image_index))
                self.deactivate_button(self.identical_btn)
            #move to Singles
            self._get_image_object(self.right_image_index).cluster = "Singles"
            if self._get_image_object(self.right_image_index) not in self.singles.images:
                self.singles.images.append(self._get_image_object(self.right_image_index))
            self.right_cluster_label.config(text = "Cluster : Singles")
 

    def cluster_validation_identical (self):
        """During cluster validation stage, mark left and right images identical
        - the right tick turn green (means checked)
        - add right image to the hashmap cluster.identical
        - add current image to cluster.matches + activate match button
        - if previously in cluster.nomatches, remove it & deactivate nomatch button

        - if the two images are already marked identical, click this button will delist them from identicals
        """
        if self.right_image_index < len(self.cluster.images):
            #add to checked
            self.current_stage.images_checked.add(self._get_image_name(self.right_image_index))
            self.change_tick_color ("right", checked = True)
            left, right = self._get_image_object(self.left_image_index), self._get_image_object(self.right_image_index)

            if self._is_identical(left,right):
                #delist form identicals
                self._remove_from_identicals(left,right)
                self.deactivate_button(self.identical_btn)

            else:
                #add to identicals
                self._add_to_identicals (left,right)
                self.activate_button(self.identical_btn)
                #add to matches
                self.cluster_validation_match()

    def cluster_validation_best_image (self):
        """During cluster validation, mark right image the best image of the cluster
        - The right image has to be a match to the left image
        - Make the right image cluster.best_image
        - Swap the left and right images
        """

        #if left and right are already matched
        if self._get_image_object(self.right_image_index) in self.cluster.matches:
            self.cluster.matches.remove(self._get_image_object(self.right_image_index)) #remove right
            self.cluster.matches.add(self._get_image_object(self.left_image_index)) #add left

        # if left and right are already unmatched
        if self._get_image_object(self.right_image_index) in self.cluster.nomatches:
            self.cluster.nomatches.remove(self._get_image_object(self.right_image_index)) #remove right
            self.cluster.nomatches.add(self._get_image_object(self.left_image_index)) #add left

        #swap attributes
        best_image = self.right_image
        best_image_index = self.right_image_index

        self.cluster.best_image = best_image

        self.right_image = self.left_image
        self.right_image_index = self.left_image_index

        self.left_image = self.cluster.best_image
        self.left_image_index = best_image_index

        #update image info display
        self.left_image_name_label.config(text = "Name : " + self.cluster.images[self.left_image_index].name)
        self.left_cluster_label.config(text = "Cluster : " + self.cluster.images[self.left_image_index].cluster)

        self.right_image_name_label.config(text = "Name : " + self.cluster.images[self.right_image_index].name)
        self.right_cluster_label.config(text = "Cluster : " + self.cluster.images[self.right_image_index].cluster)

        #swap pictures
        self.right_image.grid_forget()
        self.left_image.grid_forget()
        self.add_images(self.left_image_index, self.right_image_index)


    def create_validation_UI (self):

        #initialize left and right images
        self.left_image = self.add_filler(30,30, 0, 1, 1, 1, self.root, sticky = "w")
        _ = self.add_filler(1, 1, 1, 0, 1, 4, self.root, sticky = "w") #divider
        self.right_image = self.add_filler(30,30, 2, 1, 1, 1, self.root, sticky = "w")

        # menu bar
        right_menu_bar = self.add_frame(2, 0, 1, 1, self.root)
        right_menu_bar.rowconfigure(0, weight=1)
        right_menu_bar.columnconfigure(1, weight=1)
        _ = self.add_filler(1,1, 0, 0, 1, 1, right_menu_bar, sticky= "w")
        self.undo_btn = self.add_button("Undo", None, 2, 3, 1, 0, 1, 1, right_menu_bar, sticky = "e")
        self.open_btn = self.add_button("Open", self.browse_files, 2, 3, 2, 0, 1, 1, right_menu_bar, sticky = "e")
        self.save_btn = self.add_button("Save", None, 2, 3, 3, 0, 1, 1, right_menu_bar, sticky = "e")
        self.exit_btn = self.add_button("Exit", self.root.quit, 2, 3, 4, 0, 1, 1, right_menu_bar, sticky = "e")

        left_menu_bar = self.add_frame(0, 0, 1, 1, self.root)
        left_menu_bar.columnconfigure(1, weight=1)
        self.project_title_label = self.add_text("Project Title: ", 0, 0, 1, 1, left_menu_bar, sticky= "w")
        self.current_stage_label = self.add_text("Current Stage: ", 0, 1, 1, 1, left_menu_bar, sticky= "w")

        # image info
        self.left_info_bar = self.add_frame(0, 2, 1, 1, self.root)
        self.left_info_bar.grid_propagate(0)
        self.left_info_bar.columnconfigure(1, weight=1)
        self.left_image_name_label = self.add_text("Name : ", 0, 0, 1, 1, self.left_info_bar, sticky= "w")
        self.left_cluster_label = self.add_text("Cluster : ", 0, 1, 1, 1, self.left_info_bar, sticky= "w")

        self.right_info_bar = self.add_frame(2, 2, 1, 1, self.root)
        self.right_info_bar.grid_propagate(0)
        self.right_info_bar.columnconfigure(2, weight=1)

        self.right_image_name_label = self.add_text("Name : ", 0, 0, 1, 1, self.right_info_bar, sticky="w")
        self.right_cluster_label = self.add_text("Cluster : ", 0, 1, 1, 1, self.right_info_bar, sticky="w")

        self.right_tick = self.add_filler(1, 1, 1, 0, 1, 1, self.right_info_bar, sticky = "e")
        #navigation buttons
        self.prev_btn = self.add_button("Prev", self.load_prev_image, 4, 4, 2, 0, 1, 2, self.right_info_bar, sticky="e")
        self.next_btn = self.add_button("Next", self.load_next_image, 4, 4, 3, 0, 1, 2, self.right_info_bar, sticky="e")



        # action buttons
        action_bar = self.add_frame(2, 3, 1, 1, self.root)
        action_bar.rowconfigure(0, weight=1)
        for i in range(4):
            action_bar.columnconfigure(i, weight=1)
        self.match_btn = self.add_button("Match", self.cluster_validation_match, 2, 4, 0, 0, 1, 1, action_bar)
        self.no_match_btn = self.add_button("No Match", self.cluster_validation_no_match, 2, 4, 1, 0, 1, 1, action_bar)
        self.identical_btn = self.add_button("Identical", self.cluster_validation_identical, 2, 4, 2, 0, 1, 1, action_bar)
        self.best_image_btn = self.add_button("Best Image", self.cluster_validation_best_image, 2, 4, 3, 0, 1, 1, action_bar)


        #option bar
        option_bar = self.add_frame(0, 3, 1, 1, self.root, "w")
        option_bar.columnconfigure(0, weight=1)
        option_bar.rowconfigure(0, weight=1)
        self.single_option_label = self.add_text("When unmatched, move which image to Singles: ", 0, 0, 1, 1, option_bar, "w")

        r = tk.IntVar()
        r.set(0)
        self.left_option_button = tk.Radiobutton(option_bar, text = "left", variable = r, value = 0)
        self.right_option_button = tk.Radiobutton(option_bar, text = "right", variable = r, value = 1)
        self.left_option_button.grid(column = 0, row = 1, columnspan= 1 ,rowspan= 1, sticky= "w")
        self.right_option_button.grid(column = 0, row = 2, columnspan= 1 ,rowspan= 1, sticky= "w")

    def start (self):
        self.create_validation_UI()
        self.root.mainloop()

MainUI().start()

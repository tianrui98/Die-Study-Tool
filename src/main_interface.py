from src.objects import *
import src.progress as progress
from src.root_logger import *
from src.UI import UI
from src.identical_interface import IdenticalUI
import tkinter as tk
from tkinter.constants import CENTER, RAISED, RIDGE, VERTICAL
from PIL import Image, ImageTk
import math
from tkinter import filedialog, messagebox
import os
from tkinter import font

class MainUI(UI):
    def __init__(self):
        super().__init__(0.7)

#%% Shortcuts

    def _add_to_identicals (self, left_image_name, right_image_name):
        found = False
        for s in self.cluster.identicals:
            if left_image_name in s:
                s.add(right_image_name)
                found = True

        if not found:
            self.cluster.identicals.append(set([left_image_name, right_image_name]))

    def _remove_from_identicals (self, left_image_name, right_image_name):
        for s in self.cluster.identicals:
            if left_image_name in s:
                s.remove(right_image_name)

    def _is_identical(self, left_image_name, right_image_name):
        for s in self.cluster.identicals:
            if left_image_name in s and right_image_name in s:
                return True
        return False

    def _update_cluster_label(self):
        right_cluster_label = self._get_image_object(self.right_image_index).cluster
        if len(right_cluster_label) > 40:
            right_cluster_label = right_cluster_label[:40] + "..."
        self.right_cluster_label.config(text = "Cluster : " + right_cluster_label)

        left_cluster_label = self._get_image_object(self.left_image_index).cluster
        if len(left_cluster_label) > 40:
            left_cluster_label = left_cluster_label[:40] + "..."
        self.left_cluster_label.config(text = "Cluster : " + left_cluster_label)

    def _update_image_label(self):
        if self._get_image_object(self.right_image_index):
            right_image_label = self._get_image_object(self.right_image_index).name
        else:
            right_image_label = ""
        if len(right_image_label ) > 40:
            right_image_label  = right_image_label [:40] + "..."
        self.right_image_name_label .config(text = "Name : " + right_image_label )

        left_image_label = self._get_image_object(self.left_image_index).name
        if len(left_image_label) > 40:
            left_image_label = left_image_label[:40] + "..."
        self.left_image_name_label.config(text = "Name : " + left_image_label)

    def _has_been_checked(self, image_name):
        return image_name in self.cluster.matches or image_name in self.cluster.nomatches

#%% Visuals and Aesthetics
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

    def initialize_image_display(self):
        """initialize left and right image display"""

        best_image_index = self.cluster.get_best_image_index()
        if best_image_index == 0:
            self.left_image_index = 0
            self.right_image_index = 1
        else:
            self.left_image_index = best_image_index
            self.right_image_index = 0

        #skip the image already compared with left image
        while self.stage.stage_number > 0 and self.right_image_index < len(self.cluster.images) and self._get_image_name(self.right_image_index) in self.stage.past_comparisons[self._get_image_name(self.left_image_index)]:
            #mark them compared
            self.cluster.compared_before.add(self._get_image_name(self.right_image_index))
            #skip the right image
            logger.info("Skip already compared {}".format(self._get_image_name(self.right_image_index)))
            self.right_image_index = min(len(self.cluster.images), self.right_image_index + 1)

        #skip the index of left image
        if self.right_image_index == self.left_image_index:
            self.right_image_index = min(len(self.cluster.images), self.right_image_index + 1)

        self.project_title_label.config(text = str("Project Title: " + self.project_name))
        self.stage_label.config(text = str("Current Stage: " + self.stage.name))

        self.left_image.grid_forget()
        self.right_image.grid_forget()

        self.left_image, self.right_image = self.add_images(self.left_image_index, self.right_image_index)

        #update image info display
        self._update_image_label()
        self._update_cluster_label()
        self.update_icon_button_color()


    def add_images (self, left_image_number, right_image_number):
        """Add left and right images at once

        Args:
            left_image_number ([int]): index of image in self.cluster.images
            right_image_number ([int]): index of image in self.cluster.images

        Returns:
            TK Widget: left and right image widgets
        """
        left_path = self._get_image_address(left_image_number)
        left_image = self.add_image(left_path, 0, 1, 1, 1, self.root, sticky = "we")
        right_path = self._get_image_address(right_image_number)
        right_image = self.add_image(right_path, 1, 1, 1, 1, self.root, sticky = "we")

        #initialize tick and button style
        if self._has_been_checked(self._get_image_name(right_image_number)):
            self.change_tick_color("right", True)
        else:
            self.change_tick_color("right", False)

        if self._get_image_name(right_image_number) in self.cluster.matches:
            #the pair has been previously matched
            self.activate_button(self.match_btn)

        return left_image, right_image

    def change_tick_color (self, side, checked):
        """turn the "check" icon green or grey

        Args:
            tick_widget ([type]): [description]
            checked ([bool]): whether the image has been checked
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
        #disable best image and identical button if stage is not 0
        if self.stage.stage_number != 0:
            # self.identical_btn["state"] = "disabled"
            self.best_image_btn["state"] = "disabled"
        else:
            # self.identical_btn["state"] = "normal"
            self.best_image_btn["state"] = "normal"

        #the pair has been previously matched
        if self._get_image_name(self.right_image_index) in self.cluster.matches:
            self.activate_button(self.match_btn)
            self.change_tick_color("right", True)

        else:
            self.deactivate_button(self.match_btn)
            self.change_tick_color("right", False)

        #if the pair has been unmatched:
        if self._get_image_name(self.right_image_index) in self.cluster.nomatches:
            self.activate_button(self.no_match_btn)
            self.change_tick_color("right", True)
        else:
            self.deactivate_button(self.no_match_btn)

        #if the pair are identicals:
        # if self._is_identical(self._get_image_name(self.left_image_index), self._get_image_name(self.right_image_index)):
            # self.activate_button(self.identical_btn)
        # else:
        #     self.deactivate_button(self.identical_btn)


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
        self.stage = Stage(0, self.progress_data[self.project_address])

        #open the first cluster
        self.cluster = self._open_first_cluster()

        #initialize image display
        self.initialize_image_display()

        #close pop-up
        self.open_window.quit()
        self.open_window.destroy()


        logger.info(f"_____CREATE DEMO PROJECT_____")
        return None

    def choose_project(self):
        self.progress_data = progress.checkout_progress()
        existing_projects = {d.split('/')[-1] for d in list(self.progress_data.keys())}
        if not existing_projects:
            return
        self.create_choose_project_window(existing_projects)
        self.project_address = os.getcwd() + "/projects/" + self.project_name

        self.progress_data, self.stage, self.cluster = progress.load_progress(self.project_address)

        logger.info(f"Open project {self.project_name} at stage {self.stage.stage_number} ")
        if self.stage.stage_number < 4:
            self.initialize_image_display()
        else:
            #start identical UI
            self.root.withdraw()
            UI = IdenticalUI(project_name=self.project_name, project_address=self.project_address, progress_data= self.progress_data, cluster = self.cluster, stage = self.stage, root= self.root)
            UI.start()

    def browse_files(self):
        """Let user choose which new project/folder to start working on
        pass the directory name to the class
        show images
        """
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

        self.project_name = os.path.basename(dirname)
        self.project_address, self.progress_data = progress.start_new_project(dirname, self.project_name)
        self.stage = Stage(0, self.progress_data[self.project_address])

        #open the first cluster
        self.cluster = self._open_first_cluster()

        #initialize image display
        self.initialize_image_display()

        #close pop-up
        self.open_window.destroy()

        logger.info("_____Create new project{}_____".format(self.project_name))
        return None

    def load_next_image (self):
        """Change right image. Erase old image, Add the next in line image. function for "next" button

        """
        self.right_image_index = min(len(self.cluster.images), self.right_image_index + 1)
        #skip the image already compared with left image
        while self.stage.stage_number > 0 and self.right_image_index < len(self.cluster.images) and (self.right_image_index == self.left_image_index or  self._get_image_name(self.right_image_index) in self.stage.past_comparisons[self._get_image_name(self.left_image_index)]):
                    #skip the index of left image
            if self.right_image_index == self.left_image_index:
                self.right_image_index = min(len(self.cluster.images), self.right_image_index + 1)
            else:
                #mark them compared before
                self.cluster.compared_before.add(self._get_image_name(self.right_image_index))
                #skip the right image
                logger.info("Skip already compared {}".format(self._get_image_name(self.right_image_index)))
                self.right_image_index = min(len(self.cluster.images), self.right_image_index + 1)


        self.right_image.grid_forget()

        if self.right_image_index < len(self.cluster.images):
            new_image_path = self._get_image_address(self.right_image_index)
            self.right_image = self.add_image(new_image_path, 1, 1, 1, 1, self.root, sticky = "we")
            self._update_cluster_label()
            self.update_icon_button_color ()

        else:
            image = Image.open("images/end.png")
            iw, ih = int(image.width), int(image.height)
            h = int(self.root.winfo_height() * 0.7)
            image = image.resize((math.ceil(h/ih * iw), h), Image. ANTIALIAS)
            img = ImageTk.PhotoImage(image)
            img_label = tk.Label(self.root, image=img)
            img_label.image = img
            img_label.grid(column=1,
                        row=1,
                        columnspan=1,
                        rowspan=1,
                        sticky="we")
            self.right_image = img_label
            new_cluster_label = ""
            self.change_tick_color("right", False)
            self.deactivate_button(self.match_btn)
            self.deactivate_button(self.no_match_btn)
            self.right_cluster_label.config(text = "Cluster: " + new_cluster_label)

        #update image labels
        self._update_image_label()

        #check for completion at the last image
        if self.right_image_index == len(self.cluster.images):
            self.check_completion_and_move_on()
        return None

    def load_prev_image (self):
        """ change right image
        When user reach the index 1 image, can't move forward anymore

        """
        curr_right_image_index = self.right_image_index
        self.right_image_index = max(0, self.right_image_index - 1)
        while self.stage.stage_number > 0 and self.right_image_index > 0 and (self.right_image_index == self.left_image_index or self._get_image_name(self.right_image_index) in self.stage.past_comparisons[self._get_image_name(self.left_image_index)]):
            if self.right_image_index == self.left_image_index:
                if self.left_image_index == 0:
                    self.right_image_index = curr_right_image_index
                else:
                    self.right_image_index = max(0, self.right_image_index - 1)
            else:
                self.cluster.compared_before.add(self._get_image_name(self.right_image_index))
                logger.debug("Skip already compared {}".format(self._get_image_name(self.right_image_index)))
                self.right_image_index = max(0, self.right_image_index - 1)

        if self.right_image_index == 0 and (self.right_image_index == self.left_image_index or self._get_image_name(self.right_image_index) in self.stage.past_comparisons[self._get_image_name(self.left_image_index)]):
            self.right_image_index = curr_right_image_index

        self.right_image.grid_forget()
        if self.right_image_index >= 0:
            new_image_path = self._get_image_address(self.right_image_index)
            self.right_image = self.add_image(new_image_path, 1, 1, 1, 1, self.root, sticky = "we")
            self._update_image_label()
            self._update_cluster_label()
            self.update_icon_button_color ()

        return None

    def mark_match (self):
        """During cluster validation stage, match left and right image
        - the right tick turn green (means checked)
        - the match button's fg turn orange
        - the right image object added to cluster.matchs
        - take object out from cluster.nomatches if init

        """
        if self.right_image_index < len(self.cluster.images):
            self.change_tick_color ("right", checked = True)
            self.activate_button(self.match_btn)

            if self._get_image_name(self.right_image_index) not in self.cluster.compared_before:
                self.cluster.matches.add(self._get_image_name(self.right_image_index))
                #delist from nomatches
                if self._get_image_name(self.right_image_index) in self.cluster.nomatches:
                    self.cluster.nomatches.remove(self._get_image_name(self.right_image_index))
                    self.deactivate_button(self.no_match_btn)
                logger.info("Match {} to cluster {}".format(self._get_image_name(self.right_image_index),self.cluster.name))


    def mark_no_match (self):
        """During cluster validation stage, unmatch left and right image
        - the right tick turn green (means checked)
        - the unmatch button's fg turn orange
        - the right image object added to cluster.unmatchs
        - remove right from cluster.matches
        - update right_cluster_label to "Singles"
        - update the image's cluster to singles

        """


        if self.right_image_index < len(self.cluster.images):
            self.change_tick_color ("right", checked = True)
            self.activate_button(self.no_match_btn)

            if self._get_image_name(self.right_image_index) not in self.cluster.compared_before:
                self.cluster.nomatches.add(self._get_image_name(self.right_image_index))
                #delist from matches
                if self._get_image_name(self.right_image_index) in self.cluster.matches:
                    self.cluster.matches.remove(self._get_image_name(self.right_image_index))
                    self.deactivate_button(self.match_btn)
                #delist from identicals
                if self._is_identical(self._get_image_name(self.left_image_index), self._get_image_name(self.right_image_index)):
                    self._remove_from_identicals (self._get_image_name(self.left_image_index), self._get_image_name(self.right_image_index))
                    # self.deactivate_button(self.identical_btn)

            logger.info("Unmatch {} from cluster {}".format(self._get_image_name(self.right_image_index), self.cluster.name))



    def mark_identical (self):
        """During cluster validation stage, mark left and right images identical
        - the right tick turn green (means checked)
        - add right image to the hashmap cluster.identical
        - add current image to cluster.matches + activate match button
        - if previously in cluster.nomatches, remove it & deactivate nomatch button

        - if the two images are already marked identical, click this button will delist them from identicals
        """
        if self.right_image_index < len(self.cluster.images):

            self.change_tick_color ("right", checked = True)
            left, right = self._get_image_name(self.left_image_index), self._get_image_name(self.right_image_index)

            if self._is_identical(left,right):
                #delist form identicals
                self._remove_from_identicals(left,right)
                # self.deactivate_button(self.identical_btn)

            else:
                #add to identicals
                self._add_to_identicals (left,right)
                # self.activate_button(self.identical_btn)
                #add to matches
                self.mark_match()

            logger.info("Mark {} identical to {}".format(self._get_image_name(self.right_image_index), self._get_image_name(self.right_image_index)))

    def mark_best_image (self):
        """During cluster validation, mark right image the best image of the cluster
        - If the two images were marked unmatched, no effect
        - Make the right image cluster.best_image
        - Swap the left and right images
        """
        # if right image is already classified as single, no effect
        if self.stage.stage_number > 0 or self._get_image_name(self.right_image_index) in self.cluster.nomatches or self.right_image_index >= len(self.cluster.images):
            return None

        #swap attributes
        best_image = self.right_image
        best_image_index = self.right_image_index

        self.cluster.best_image = self._get_image_object(best_image_index)

        self.right_image = self.left_image
        self.right_image_index = self.left_image_index

        self.left_image =best_image
        self.left_image_index = best_image_index

        #update image info display
        self._update_image_label()
        self._update_cluster_label()

        #swap pictures
        self.right_image.grid_forget()
        self.left_image.grid_forget()
        self.add_images(self.left_image_index, self.right_image_index)

        #if new right image has been matched to anything in the cluster before -> mark checked & match
        if len(self.cluster.matches) > 0:
            self.change_tick_color("right", True)
            self.activate_button(self.match_btn)
            self.cluster.matches.add(self._get_image_name(self.right_image_index))
            if self._get_image_name(self.left_image_index) in self.cluster.matches:
                self.cluster.matches.remove(self._get_image_name(self.left_image_index))

        else:
            self.change_tick_color("right", False)
            self.deactivate_button(self.match_btn)

        #swap the positions of the old best image (now right image) with the old right image (now left image) in the list
        self.cluster.images = self._swap_positions(self.cluster.images, self.right_image_index, self.left_image_index)
        #update left and right images' indices
        curr_left_index = self.left_image_index
        curr_right_index = self.right_image_index
        self.left_image_index = curr_right_index
        self.right_image_index = curr_left_index
        logger.info("Make {} best image for cluster {}".format(self._get_image_name(self.right_image_index), self.cluster.name))

    def check_completion_and_move_on (self):
        """This function is called when user clicks "next" while at the last image
        !!! only mark cluster complete if user clicks ok"""

        if progress.check_cluster_completion(self.cluster,self.stage):
            self.stage = progress.mark_cluster_completed(self.cluster, self.stage, self.progress_data[self.project_address]["clusters"])

        if progress.check_part1_completion(self.cluster, self.stage, self.project_address):
            logger.info("_____PART 1 COMPLETED_____")
            logger.info(str(self.progress_data))
            message = "You have completed the current *STAGE*."
            response = self.create_save_progress_window(message)
            if response:
                self.progress_data, self.stage = progress.save_progress_data(self.project_address, self.stage,self.cluster,self.progress_data)
                self.cluster, self.stage = progress.create_new_objects(self.cluster, self.stage, self.project_address, self.progress_data)
                #start identical UI
                self.root.withdraw()
                UI = IdenticalUI(project_name=self.project_name, project_address=self.project_address, progress_data= self.progress_data, cluster = self.cluster, stage = self.stage, root= self.root)
                UI.start()
                return None
            else:
                self.stage = progress.unmark_cluster_completed(self.cluster, self.stage, self.progress_data[self.project_address]["clusters"])
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
                self.stage = progress.mark_cluster_completed(self.cluster, self.stage, self.progress_data[self.project_address]["clusters"])

                self.progress_data, self.stage = progress.save_progress_data(self.project_address, self.stage,self.cluster,self.progress_data)
                self.cluster, self.stage = progress.create_new_objects(self.cluster, self.stage, self.project_address, self.progress_data)

                if self.cluster:
                    #if next cluster has only 1 image, skip it & recurse
                    if len(self.cluster.images) <= 1:
                        logger.info("----SKIP {}----".format(self.cluster.name))
                        self.stage = progress.mark_cluster_completed(self.cluster,self.stage, self.progress_data[self.project_address]["clusters"])
                        self.progress_data, self.stage = progress.save_progress_data(self.project_address, self.stage,self.cluster,self.progress_data)
                        self.cluster, self.stage = progress.create_new_objects(self.cluster, self.stage, self.project_address, self.progress_data)
                        self.check_completion_and_move_on ()
                    else:
                        self.initialize_image_display()
                if "stage" in message:
                    logger.info(str(self.progress_data))
            else:
                self.stage = progress.unmark_cluster_completed(self.cluster, self.stage, self.progress_data[self.project_address]["clusters"])
        self.root.after(1, lambda: self.root.focus_force())

    def create_UI (self):

        #initialize left and right images
        self.left_image = self.add_filler(self.image_height_char,self.image_height_char, 0, 1, 1, 1, self.root, sticky = "w", content = "", color = None)
        self.right_image = self.add_filler(self.image_height_char,self.image_height_char, 1, 1, 1, 1, self.root, sticky = "w", content = "", color = None)

        # menu bar
        right_menu_bar = self.add_frame(self.button_frame_height, self.button_frame_width, 1, 0, 1, 1, self.root, "e")
        self.open_btn = self.add_button("Open", self.create_open_window, 2, 3, 1, 0, 1, 1, right_menu_bar, sticky = "e")
        self.export_btn = self.add_button("Export", self.export, 2, 3, 2, 0, 1, 1, right_menu_bar, sticky = "e")
        self.save_btn = self.add_button("Save", self.save, 2, 3, 3, 0, 1, 1, right_menu_bar, sticky = "e")
        self.exit_btn = self.add_button("Exit", self.exit, 2, 3, 4, 0, 1, 1, right_menu_bar, sticky = "e")

        left_menu_bar = self.add_frame(self.button_frame_height, self.button_frame_width,0, 0, 1, 1, self.root, "we")
        # left_menu_bar.columnconfigure(1, weight=1)
        self.project_title_label = self.add_text("Project Title: ", 0, 0, 1, 1, left_menu_bar, sticky= "w")
        self.stage_label = self.add_text("Current Stage: ", 0, 1, 1, 1, left_menu_bar, sticky= "w")

        # image info
        self.left_info_bar = self.add_frame(self.button_frame_height, self.button_frame_width,0, 2, 1, 1, self.root)
        # self.left_info_bar.grid_propagate(0)
        # self.left_info_bar.columnconfigure(1, weight=1)
        self.left_image_name_label = self.add_text("Name : ", 0, 0, 1, 1, self.left_info_bar, sticky= "w")
        self.left_cluster_label = self.add_text("Cluster : ", 0, 1, 1, 1, self.left_info_bar, sticky= "w")
        _ = self.add_filler(4, 4, 2, 0, 1, 2, self.left_info_bar, "e", "", None)

        self.right_info_bar = self.add_frame(self.button_frame_height, self.button_frame_width,1, 2, 1, 1, self.root)
        self.right_info_bar.grid_propagate(0)
        self.right_info_bar.columnconfigure(2, weight=1)

        self.right_image_name_label = self.add_text("Name : ", 0, 0, 1, 1, self.right_info_bar, sticky="w")
        self.right_cluster_label = self.add_text("Cluster : ", 0, 1, 1, 1, self.right_info_bar, sticky="w")

        self.right_tick = self.add_filler(1, 1, 1, 0, 1, 1, self.right_info_bar, sticky = "e")

        #navigation buttons
        self.prev_btn = self.add_button("◀", self.load_prev_image, 4, 4, 2, 0, 1, 2, self.right_info_bar, sticky="e")
        self.next_btn = self.add_button("▶", self.load_next_image, 4, 4, 3, 0, 1, 2, self.right_info_bar, sticky="e")

        # action buttons
        action_bar = self.add_frame(self.button_frame_height, self.button_frame_width,1, 3, 1, 1, self.root, "se")
        action_bar.rowconfigure(0, weight=1)
        for i in range(4):
            action_bar.columnconfigure(i, weight=1)

        action_button_height = 4

        self.best_image_btn = self.add_button("Best Image", self.mark_best_image, action_button_height, 8, 0, 0, 1, 1, action_bar,"se")
        self.no_match_btn = self.add_button("No Match", self.mark_no_match, action_button_height, 8, 1, 0, 1, 1, action_bar, "se")
        self.match_btn = self.add_button("Match", self.mark_match, action_button_height, 8, 2, 0, 1, 1, action_bar, "se")

    def start(self):
        self.create_UI()
        #key binding
        self.root.bind('<Right>', lambda event: self.load_next_image())
        self.root.bind('<Left>', lambda event: self.load_prev_image())
        self.root.bind('m', lambda event: self.mark_match())
        self.root.bind('n', lambda event: self.mark_no_match())
        self.root.bind('b', lambda event: self.mark_best_image())

        try:
            self.root.mainloop()
        except:
            logger.error("====Error in main loop====")
# %%

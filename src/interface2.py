from src.objects import *
import src.progress as progress
from src.root_logger import *
from src.UI import UI
import tkinter as tk
from tkinter.constants import CENTER, RAISED, RIDGE
from PIL import Image, ImageTk
from tkinter import Toplevel, filedialog, messagebox
from tkinter import font

class IdenticalUI (UI):

    def __init__(self):
        super().__init__(0.48)

    def create_UI (self):

        #TODO replace None with actual functions
        # menu bar

        self.left_main_frame_width_pixel = int(self.initial_width * 0.68)
        self.right_main_frame_width_pixel = int(self.initial_width * 0.28)
        self.main_frame_height = int(self.initial_height * 0.9)

        left_menu_bar = self.add_frame(int(self.initial_height * 0.1), int(self.initial_width * 0.5),0, 0, 1, 1, self.root, "w")
        self.project_title_label = self.add_text("Project Title: ", 0, 0, 1, 1, left_menu_bar, sticky= "w")
        self.stage_label = self.add_text("Current Stage: ", 0, 1, 1, 1, left_menu_bar, sticky= "w")

        right_menu_bar = self.add_frame(int(self.initial_height * 0.1), int(self.initial_width * 0.5),1, 0, 1, 1, self.root, "e")
        self.open_btn = self.add_button("Open", None, 2, 3, 1, 0, 1, 1, right_menu_bar, sticky = "e")
        self.undo_btn = self.add_button("Export", None, 2, 3, 2, 0, 1, 1, right_menu_bar, sticky = "e")
        self.save_btn = self.add_button("Save", None, 2, 3, 3, 0, 1, 1, right_menu_bar, sticky = "e")
        self.exit_btn = self.add_button("Exit", None, 2, 3, 4, 0, 1, 1, right_menu_bar, sticky = "e")

        #left main frame: display coin images Height: 0.8 * window, width: 0.7 * window width
        self.left_main_frame = self.add_frame(self.main_frame_height, self.left_main_frame_width_pixel, 0, 1, 1, 3, self.root, "nsew")
        #right main frame: display current identical groups
        self.right_main_frame = self.add_frame(self.main_frame_height, self.right_main_frame_width_pixel, 1, 1, 1, 3, self.root, "nsew")

        #Left main frame can display max 6 pictures. 
        self.image_frames = []
        for i in range(6):
            col = i % 3
            row = i // 3
            image_filler = self.add_image("images/blank.png", col, row, 1, 1, self.left_main_frame, "nsew", int(self.main_frame_height * 0.5))
            self.image_frames.append(image_filler)

        #a small image for easy comparison
        self.right_image_window = self.add_image("images/blank.png", 0,0,1,1,self.right_main_frame, "we", int(self.right_main_frame_width_pixel * 0.7))
        identical_header = self.add_text("Identical coins: ", 0, 1, 1, 1, self.right_main_frame, "w")

        # a list for all the identicals that are added to the group
        coin_list = []

        self.scrollbar = tk.Scrollbar(self.right_main_frame, orient = tk.VERTICAL)
        self.identical_list_box = tk.Listbox(self.right_main_frame, 
                                            height = self._pixel_to_char(int(self.main_frame_height * 0.1)),
                                            width = self._pixel_to_char(int(self.right_main_frame_width_pixel * 0.8)),
                                            yscrollcommand= self.scrollbar.set)


        self.scrollbar.config(command = self.identical_list_box.yview)
        self.scrollbar.grid(column = 1, row = 2, sticky = "ns")

        for item in coin_list:
            self.identical_list_box.insert(tk.END, item)
        self.identical_list_box.grid(column = 0, row = 2, columnspan= 1, rowspan= 1, sticky = "we" )

        #buttons
        list_button_frame = self.add_frame(5,self.right_main_frame_width_pixel * 0.8, 0, 3,2,1,self.right_main_frame, "w")
        _ = self.add_button("Remove from list", None, 2, 13, 0, 3, 1,1, list_button_frame, "w")
        _ = self.add_button("Confirm current list", None, 2,13, 1, 3, 1,1, list_button_frame, "e")

        _ = self.add_button("Finish current cluster", None, 3, 15, 0, 4, 2, 1, self.right_main_frame, "we" )

        prev_next_frame = self.add_frame(5,self.right_main_frame_width_pixel * 0.8, 0, 5, 2,1,self.right_main_frame, "w")
        _ = self.add_button("Prev", None, 4, 4, 0, 0, 1, 1, prev_next_frame , sticky="w")
        _ = self.add_button("Next", None, 4, 4, 1, 0, 1, 1, prev_next_frame , sticky="w")


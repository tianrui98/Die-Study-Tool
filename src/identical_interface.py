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

    def __init__(self, project_name = "", project_address = "", progress_data = {}, cluster = None, stage = None):
        super().__init__(0.48, project_name, project_address, progress_data)

        #the first 6 images will be on page 0, the next 6 on page 1 etc.
        self.current_page = 0
        self.cluster = cluster
        self.stage = stage

    #functionality
    def _add_image_to_identical (self, image_object):
        """add the image associated with the "add" button to the identical list
        function triggered by pressing "add" button.
        """
        if not image_object:
            return None
        if image_object.name in self.identical_coin_dict:
            return None
        self.identical_coin_dict[image_object.name] = image_object
        self.identical_list_box.insert(tk.END, image_object.name)
        #display current image in the small window if it's the first on the list
        if len(self.identical_coin_dict) == 1:
            self.right_image_window.grid_forget()
            self.right_image_window = self.add_image(image_object.address, 0,0,1,1,self.right_main_frame, "we", int(self.right_main_frame_width_pixel * 0.7))

    def _add_function_0(self):
        image_object = self.image_on_display[0][0]
        self._add_image_to_identical(image_object)

    def _add_function_1(self):
        image_object = self.image_on_display[1][0]
        self._add_image_to_identical(image_object)

    def _add_function_2(self):
        image_object = self.image_on_display[2][0]
        self._add_image_to_identical(image_object)

    def _add_function_3(self):
        image_object = self.image_on_display[3][0]
        self._add_image_to_identical(image_object)

    def _add_function_4(self):
        image_object = self.image_on_display[4][0]
        self._add_image_to_identical(image_object)

    def _add_function_5(self):
        image_object = self.image_on_display[5][0]
        self._add_image_to_identical(image_object)

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

    def remove_image_from_list (self):
        """Remove a selected item from the identical list.
        If the removed coin is the first one on the list. The second one will be displayed.
        If the removed coin is the only one on the list. The display window will be blank.
        """
        image_name = self.identical_list_box.get(tk.ANCHOR)
        if not image_name in self.identical_coin_dict:
            return None
        self.identical_coin_dict.pop(image_name)
        self.identical_list_box.delete(tk.ANCHOR)

        if len(self.identical_coin_dict) > 0 :
            default_image_name = self.identical_list_box.get(0)
            default_image_object = self.identical_coin_dict[default_image_name]
            self.right_image_window.grid_forget()
            self.right_image_window = self.add_image(default_image_object.address, 0,0,1,1,self.right_main_frame, "we", int(self.right_main_frame_width_pixel * 0.7))

        else:
            self.right_image_window.grid_forget()
            self.right_image_window = self.add_image("images/blank.png", 0,0,1,1,self.right_main_frame, "we", int(self.right_main_frame_width_pixel * 0.7))

    def onselect(self, evt):
        """update the display window according to the image being selected

        Args:
            evt ([tkinter event]): a tkinter event
        """
        w = evt.widget
        index = int(w.curselection()[0])
        image_name = w.get(index)
        image_object = self.identical_coin_dict[image_name]
        self.right_image_window.grid_forget()
        self.right_image_window = self.add_image(image_object.address, 0,0,1,1,self.right_main_frame, "we", int(self.right_main_frame_width_pixel * 0.7))

    def confirm_current_list (self):
        """mark the images on the list identical and un-display their widgets.
        reset the identical list and display window.
        """
        pass

    #visuals
    def refresh_image_display(self) -> None:
        """show current cluster's coin images. Add the image widgets to the image_widgets dictionary"""
        for i in range(self.current_page*6, min(len(self.cluster.images), (self.current_page + 1)*6)):
            image_object = self._get_image_object(i)
            display_index = i % 6
            print(f"i = {i}, elem index = {display_index}")
            old_image_widget = self.image_on_display[display_index][1]
            old_image_widget.grid_forget()
            image_frame = self.image_frames[i]
            new_image_widget =self.add_image(image_object.address, 0, 0, 1, 1, image_frame, "n", int(self.main_frame_height * 0.49))
            self.image_on_display[display_index] = (image_object, new_image_widget)
        print(f"refresh image display, {self.image_on_display}")

    def create_UI (self):
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

        # a dictionary of identical image objects currently on the stack. Key: image name. Value: image object
        self.identical_coin_dict = {}

        # the first identical added to the list. type: image object
        self.identical_coin_ref = None

        #identical coin list box displays the names of the identical coins
        self.scrollbar = tk.Scrollbar(self.right_main_frame, orient = tk.VERTICAL)
        self.identical_list_box = tk.Listbox(self.right_main_frame, 
                                            height = self._pixel_to_char(int(self.main_frame_height * 0.1)),
                                            width = self._pixel_to_char(int(self.right_main_frame_width_pixel * 0.8)),
                                            yscrollcommand= self.scrollbar.set)

        self.scrollbar.config(command = self.identical_list_box.yview)
        self.scrollbar.grid(column = 1, row = 2, sticky = "ns")

        self.identical_list_box.grid(column = 0, row = 2, columnspan= 1, rowspan= 1, sticky = "we" )

        self.identical_list_box.bind('<<ListboxSelect>>', self.onselect)

        #Left main frame can display max 6 pictures.
        self.image_on_display = {} #key: element index (0-5), value: (image object, image widget)
        #0:(None,None),1:(None,None),2:(None,None), 3:(None,None),4:(None,None),5:(None,None)
        self.add_button_widgets = []
        self.image_frames = []

        for i in range(6):
            col = i % 3
            row = i // 3
            image_frame = self.add_frame(int(self.main_frame_height * 0.5),int(self.main_frame_height * 0.5), col, row, 1, 1, self.left_main_frame, "nsew")
            self.image_frames.append(image_frame)
            image_filler = self.add_image("images/blank.png", 0, 0, 1, 1, image_frame, "n", int(self.main_frame_height * 0.49))
            self.image_on_display[i] = (None, image_filler)
            add_function = self._add_function_n(i)
            add_identical_button = self.add_button("Add", add_function , self._pixel_to_char(int(self.main_frame_height * 0.01)), 5, 0,1,1,1, image_frame, "s")
            self.add_button_widgets.append(add_identical_button)

        print(f"initial image on display {self.image_on_display}")
        #a small image for easy comparison
        self.right_image_window = self.add_image("images/blank.png", 0,0,1,1,self.right_main_frame, "we", int(self.right_main_frame_width_pixel * 0.7))
        identical_header = self.add_text("Identical coins: ", 0, 1, 1, 1, self.right_main_frame, "w")

        #buttons
        list_button_frame = self.add_frame(5,self.right_main_frame_width_pixel * 0.8, 0, 3,2,1,self.right_main_frame, "w")
        _ = self.add_button("Remove from list", self.remove_image_from_list, 2, 13, 0, 3, 1,1, list_button_frame, "w")
        _ = self.add_button("Confirm current list", None, 2,13, 1, 3, 1,1, list_button_frame, "e")

        _ = self.add_button("Finish current cluster", None, 3, 15, 0, 4, 2, 1, self.right_main_frame, "we" )

        prev_next_frame = self.add_frame(5,self.right_main_frame_width_pixel * 0.8, 0, 5, 2,1,self.right_main_frame, "w")
        _ = self.add_button("Prev", None, 4, 4, 0, 0, 1, 1, prev_next_frame , sticky="sw")
        _ = self.add_button("Next", None, 4, 4, 1, 0, 1, 1, prev_next_frame , sticky="sw")

    def start(self):
        self.create_UI()
        self.refresh_image_display()
        try:
            self.root.mainloop()
        except:
            logger.error("====Error in main loop====")


import tkinter as tk
from PIL import Image, ImageTk
import math
import actions
from tkinter import filedialog
from tkinter.filedialog import askopenfile
import os

left_path = "/Users/rui/Desktop/Coin/Clean_Reverse_Cluster_Folder/Reverse_Clusters_1302/53/53_Clusters/53;007_53;072_53;144/53;007.jpg"
right_path = "/Users/rui/Desktop/Coin/Clean_Reverse_Cluster_Folder/Reverse_Clusters_1302/53/53_Clusters/53;007_53;072_53;144/53;072.jpg"


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
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)

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
                           command=func)
        button_text.set(content)
        button.grid(column=column,
                    row=row,
                    columnspan=columspan,
                    rowspan=rowspan,
                    sticky=sticky)
        return button

    def add_frame(self, column, row, columspan, rowspan, parent, sticky="nsew"):
        frame = tk.Frame(parent, padx=6, pady=6, bd=0)
        frame.grid(column=column,
                   row=row,
                   columnspan=columspan,
                   rowspan=rowspan,
                   sticky=sticky)

        return frame

    def add_filler(self, height, width, column, row, columspan, rowspan, parent, sticky="nsew", content = ""):
        filler = tk.Label(parent, width=width, height=height, text = content)
        filler.grid(column=column,
                    row=row,
                    columnspan=columspan,
                    rowspan=rowspan,
                    sticky=sticky)

        return filler

    def open_cluster(self):
        #TODO read log then open undone cluster
        self.cluster_name =  os.listdir(self.project_address) [0]
        self.cluster_address = os.path.join(self.project_address, self.cluster_name )
        self.cluster_images = sorted([f for f in os.listdir(self.cluster_address) if not f.startswith('.')])

    def add_images (self, left_image_number, right_image_number):
        """Add left and right images at once

        Args:
            left_image_number ([type]): index of image in self.cluster_images
            right_image_number ([type]): index of image in self.cluster_images

        Returns:
            TK Widget: left and right image widgets
        """
        left_path = os.path.join(self.cluster_address, self.cluster_images[left_image_number])
        left_image = self.add_image(left_path, 0, 1, 1, 1, self.root, sticky = "we")
        self.add_filler(1, 1, 1, 0, 1, 4, self.root) #divider
        right_path = os.path.join(self.cluster_address, self.cluster_images[right_image_number])
        right_image = self.add_image(right_path, 2, 1, 1, 1, self.root, sticky = "we")

        return left_image, right_image

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
        #update project status
        self.current_stage_label.config (text = "Current Stage: Cluster Validation")

        self.project_address = dirname
        self.open_cluster()
        self.left_image.grid_forget()
        self.right_image.grid_forget()

        #TODO: change index accordint to progress?

        self.left_image_index = 0
        self.right_image_index = 1
        self.left_image, self.right_image = self.add_images(self.left_image_index, self.right_image_index)
        return None

    def load_next_image (self, image_widget, side):
        """Erase old image, Add the next in line image. function for "next" button

        Args:
            image_widget (TK Widget): either self.left or self.right
            side (str): "left" or "right"
        """
        if side == "left":
            column = 0
            self.left_image_index = min(len(self.cluster_images), self.left_image_index + 1)
            index = self.left_image_index
        else:
            column = 2
            self.right_image_index = min(len(self.cluster_images), self.right_image_index + 1)
            index = self.right_image_index

        image_widget.grid_forget()
        if index <= len(self.cluster_images) - 1:
            new_image_path = os.path.join(self.cluster_address, self.cluster_images[index])
            image_widget = self.add_image(new_image_path, column, 1, 1, 1, self.root, sticky = "we")
        else:
            self.add_filler(30,30, 2, 1, 1, 1, self.root, content = "End of Cluster")
        return None

    def load_prev_image (self, image_widget, side):
        """Erase old image, Add the prev in line image. function for "prev" button
        When user reach the index 1 image (for right) or 0 (for left), can't move forward anymore

        Args:
            image_widget (TK Widget): either self.left or self.right
            side (str): "left" or "right"
        """

        if side == "left":
            column = 0
            self.left_image_index = max(0, self.left_image_index - 1)
            index = self.left_image_index
        else:
            column = 2
            self.right_image_index = max(1, self.right_image_index - 1)
            index = self.right_image_index

        image_widget.grid_forget()
        if index >= 0:
            new_image_path = os.path.join(self.cluster_address, self.cluster_images[index])
            image_widget = self.add_image(new_image_path, column, 1, 1, 1, self.root, sticky = "we")

        return None

    def create_validation_UI (self):

        #initialize left and right images
        self.left_image = self.add_filler(30,30, 0, 1, 1, 1, self.root)
        _ = self.add_filler(1, 1, 1, 0, 1, 4, self.root)
        self.right_image = self.add_filler(30,30, 2, 1, 1, 1, self.root)

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
        _ = self.add_filler(4,70, 1, 0, 3, 2, left_menu_bar, sticky= "e")

        # image info
        left_info_bar = self.add_frame(0, 2, 1, 1, self.root)
        left_info_bar.columnconfigure(1, weight=1)
        self.left_image_name_label = self.add_text("Name : ", 0, 0, 1, 1, left_info_bar)
        self.left_cluster_label = self.add_text("Cluster : ", 0, 1, 1, 1, left_info_bar)
        _ = self.add_filler(4,80, 1, 0, 3, 2, left_info_bar, sticky= "e")

        right_info_bar = self.add_frame(2, 2, 1, 1, self.root)
        right_info_bar.columnconfigure(1, weight=1)
        right_info_bar.columnconfigure(2, weight=1)
        self.right_image_name_label = self.add_text("Name : ", 0, 0, 1, 1, right_info_bar, sticky="w")
        self.right_cluster_label = self.add_text("Cluster : ", 0, 1, 1, 1, right_info_bar, sticky="w")
        _ = self.add_filler(4,80, 1, 0, 3, 2, right_info_bar, sticky= "e")

        #navigation bar
        self.prev_btn = self.add_button("Prev", lambda: self.load_prev_image(self.right_image, "right"), 4, 4, 4, 0, 1, 2, right_info_bar, sticky="e")
        self.next_btn = self.add_button("Next", lambda: self.load_next_image(self.right_image, "right"), 4, 4, 5, 0, 1, 2, right_info_bar, sticky="e")

        # action buttons
        action_bar = self.add_frame(2, 3, 1, 1, self.root)
        action_bar.rowconfigure(0, weight=1)
        for i in range(4):
            action_bar.columnconfigure(i, weight=1)
        self.match_btn = self.add_button("Match", None, 2, 4, 0, 0, 1, 1, action_bar)
        self.no_match_btn = self.add_button("No Match", None, 2, 4, 1, 0, 1, 1, action_bar)
        self.identical_btn = self.add_button("Identical", None, 2, 4, 2, 0, 1, 1, action_bar)
        self.best_image_btn = self.add_button("Best Image", None, 2, 4, 3, 0, 1, 1, action_bar)


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

I = MainUI()
I.create_validation_UI()
I.root.mainloop()
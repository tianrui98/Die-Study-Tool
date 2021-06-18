import tkinter as tk
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfile

left_path = "/Users/rui/Desktop/Coin/Clean_Reverse_Cluster_Folder/Reverse_Clusters_1302/53/53_Clusters/53;007_53;072_53;144/53;007.jpg"
right_path = "/Users/rui/Desktop/Coin/Clean_Reverse_Cluster_Folder/Reverse_Clusters_1302/53/53_Clusters/53;007_53;072_53;144/53;072.jpg"


class MainUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Die Study Tool")
        self.root.minsize(width=600, height=500)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)

    def browse_files(self):
        file = askopenfile(parent=self.root, mode="rb",
                           title="Choose a folder")
        if file:
            print("success")

    def add_image(self, path, column, row, columspan, rowspan):
        import math
        image = Image.open(path)
        iw, ih = int(image.width), int(image.height)
        h = 800
        image = image.resize((math.ceil(h/ih * iw), h), Image. ANTIALIAS)
        img = ImageTk.PhotoImage(image)
        img_label = tk.Label(image=img)
        img_label.image = img
        img_label.grid(column=column,
                       row=row,
                       columnspan=columspan,
                       rowspan=rowspan,
                       sticky="w")

    def add_text(self, content, column, row, columspan, rowspan):
        text = tk.Label(self.root, text=content)
        text.grid(column=column,
                  row=row,
                  columnspan=columspan,
                  rowspan=rowspan,
                  sticky="w")

    def add_button(self, content, func, height, width, column, row, columspan, rowspan):
        button_text = tk.StringVar()
        button = tk.Button(self.root,
                           textvariable=button_text,
                           height=height,
                           width=width,
                           command=func)
        button_text.set(content)
        button.grid(column=column,
                    row=row,
                    columnspan=columspan,
                    rowspan=rowspan)

    def add_frame(self, content, column, row, columspan, rowspan):
        frame = tk.LabelFrame(self.root, text=content)
        frame.grid(column=column,
                   row=row,
                   columnspan=columspan,
                   rowspan=rowspan)

    def add_frames(self):
        left_description_bar = tk.Frame(self.root, padx=5, pady=3, bd=0)
        left_description_bar.grid(column=0,
                                  row=2,
                                  columnspan= 1,
                                  rowspan = 1,
                                  stick = "w"
                                  )
        right_description_bar = tk.Frame(self.root, padx=5, pady=3, bd = 0)
        right_description_bar.grid(column=1,
                                   row=2,
                                   columnspan= 1,
                                   rowspan= 1,
                                   stick = "w")

        left_image_name = tk.Label(left_description_bar, text="Image name: ")
        left_image_name.grid(column=0,
                             row=0,
                             columnspan=1,
                             rowspan=1,
                             sticky="w")
        right_image_name = tk.Label(right_description_bar, text="Image name: ")
        right_image_name.grid(column=0,
                              row=0,
                              columnspan=1,
                              rowspan=1,
                              sticky="w")

# main interface
# canvas_width = 400
# canvas_height = 300
# canvas = tk.Canvas(root, width = canvas_width, height = canvas_height)
# canvas.grid(columnspan = 2, rowspan = 4)


I = MainUI()

# left and right images
I.add_image(left_path, 0, 1, 1, 1)
I.add_image(right_path, 1, 1, 1, 1)

# menu bar
I.add_text("Project Title: ", 0, 0, 1, 1)
I.add_button("Exit", None, 2, 3, 1, 0, 1, 1)

# image info
I.add_frames()


I.add_text("Cluster: ", 0, 3, 1, 1)

# action buttons
I.add_button("Match", None, 2, 3, 1, 3, 1, 1)

I.root.mainloop()

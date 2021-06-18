import tkinter as tk
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfile

canvas_width = 400
canvas_height = 300
left_path = "/Users/rui/Desktop/Coin/Clean_Reverse_Cluster_Folder/Reverse_Clusters_1302/53/53_Clusters/53;007_53;072_53;144/53;007.jpg"
right_path = "/Users/rui/Desktop/Coin/Clean_Reverse_Cluster_Folder/Reverse_Clusters_1302/53/53_Clusters/53;007_53;072_53;144/53;072.jpg"
content = "Project Name: "

root = tk.Tk ()
root.title("Die Study Tool")

def browse_files ():
    file = askopenfile(parent = root, mode = "rb",title = "Choose a folder")
    if file:
        print("success")

def add_image(path):
    img = ImageTk.PhotoImage(Image.open(path))
    img_label = tk.Label(image = img)
    img_label.image = img
    img_label.grid(column = 0, row = 2)

def add_text(content):
    text = tk.Label(root, text = content)
    text.grid(column = 0, row = 0)

def add_button(content,func):
    button_text = tk.StringVar()
    button = tk.Button(root,
                        textvariable= button_text,
                        height = 2,
                        width = 5,
                        command = func)
    button_text.set(content)
    button.grid(column = 1, row = 4)



canvas = tk.Canvas(root, width = canvas_width, height = canvas_height)
canvas.grid(columnspan = 2, rowspan = 5)

add_text(content)
add_image(left_path)
add_button("Open", browse_files)
root.mainloop()
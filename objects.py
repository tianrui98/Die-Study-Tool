import os

class ImgObj:
    """Class object for an image
    Updated as changes happen
    """
    def __init__(self, address, category):
        self.name = address.split("/")[-1]
        self.address = address
        self.category = category #type: Category
        self.prev_category = category #The last category it was placed in
        self.identicals = [] # List of ImgObj

class Category:
    """Class object that includes Cluster and Singles
    Updated as changes happen
    """
    def __init__ (self, folder_address):
        self.address = folder_address
        self.identicals = {} #key: name value: list of image names
        self.number = len(self.cluster_images) #number of coins

class Cluster(Category):
    """Class object for a cluster of coins
    images, best_images :Updated as changes happen
    name: updated upon saving
    """
    def __init__ (self, name = "_cluster"):
        self.name = name
        #key: image name  -  value: ImgObj
        self.images = dict((i,ImgObj(os.path.join(self.address, i), self.name )) for i in os.listdir(self.address))
        self.best_image = self.images[0] #default first image

class Singles(Category):
    """Class object for singles folder
    """
    def __init__ (self):
        self.name = "Singles"
        self.images = dict((i,ImgObj(os.path.join(self.address, i), self.name )) for i in os.listdir(self.address))

class Records:
    """Cluster and identical coin record for organizing folders & making the final excel sheet
    Updated upon saving.
    """
    def __init__ (self):
        self.clusters = [] #list of Cluster objects
        self.identicals ={} #key: image name #value: identical coins

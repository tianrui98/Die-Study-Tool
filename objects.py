import os

class ImgObj:
    """Class object for an image
    Updated as changes happen
    """
    def __init__(self, address, category_name):
        self.name = address.split("/")[-1]
        self.address = address
        self.cluster = category_name #either cluster name or "Singles"
        self.prev_cluster = category_name #The last category it was placed in
        self.identicals = [] # List of ImgObj


class Cluster:
    """Class object for a cluster of coins
    images, best_images : Updated dynamically
    name: updated upon saving
    """
    def __init__ (self, folder_address):
        self.address = folder_address
        self.name = folder_address.split("/")[-1]
        image_files = sorted([f for f in os.listdir(self.address) if not f.startswith('.')])
        self.images = [ImgObj(os.path.join(self.address, f), self.name) for f in image_files]
        self.identicals = {} #key: name value: list of image names
        self.number = len(self.images) #number of coins
        self.best_image = self.images[0] #default first image

# class Singles:
#     """Class object for singles folder
#     """
#     def __init__ (self, folder_address):
#         self.name = "Singles"
#         self.address = folder_address
#         self.images = dict((i,ImgObj(os.path.join(self.address, i), self.name )) for i in os.listdir(self.address))
#         self.identicals = {} #key: name value: list of image names
#         self.number = len(self.images) #number of coins

class Stage:
    """track progress in a stage
    "images_checked": Linked with "tick" icon
    name: "Validate Clusters", "Inspect Verified", "Verified vs Singles", "Singles vs Singles"
    """
    def __init__(self, stage_number):
        self.stages = ["Validate Clusters", "Inspect Verified", "Verified vs Singles", "Singles vs Singles"]
        self.stage_number = stage_number
        self.name = self.stages[self.stage_number]
        self.images_checked = set()

    def next_stage(self):
        """When move into the next stage, clear images checked
        """
        self.stage_number += 1
        self.name = self.stages[self.stage_number]
        self.images_checked = set() #image names

class Records:
    """Cluster and identical coin record for organizing folders & making the final excel sheet
    Updated dynamically
    """
    def __init__ (self):
        self.clusters = [] #list of Cluster objects
        self.identicals ={} #key: image name #value: identical coins

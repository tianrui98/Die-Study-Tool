import os

class ImgObj:
    """Class object for an image
    """
    def __init__(self, address, cluster):
        self.name = address.split("/")[-1]
        self.address = address
        self.cluster = cluster #Cluster class object

class Cluster:
    """Class object for a cluster of coins
    """
    def __init__ (self, folder_address, name = "_cluster"):
        self.name = name
        self.address = folder_address
        self.images = [ImgObj(i, self.name) for i in os.listdir(folder_address)]
        self.best_image = self.cluster_images[0] #default first image
        self.identicals = {} #key: name value: image names
        self.number = len(self.cluster_images) #number of coins

class Singles:
    """Class object for all single coins
    """
    def __init__ (self,folder_address):
        self.address = folder_address
        self.images = [ImgObj(i, self.name) for i in os.listdir(folder_address)]
        self.identicals = {} #key: name value: image names
        self.number = len(self.cluster_images) #number of coins

class Records:
    """Cluster and identical coin record for organizing folders & making the final excel sheet
    """
    def __init__ (self):
        self.clusters = [] #list of Cluster objects
        self.identicals ={} #key: image name #value: identical coins

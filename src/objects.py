import os
from typing import DefaultDict

class ImgObj:
    """Class object for an image
    Updated as changes happen
    """
    def __init__(self, address, category_name):
        self.name = address.split("/")[-1] #with .jpg
        self.id = self.name.split(".")[0] #without .jpg
        self.address = address
        self.cluster = category_name #either cluster name or "Singles"

class Cluster:
    """Class object for a cluster of coins
    images, best_images : Updated dynamically
    name: updated upon saving
    number: updated upon saving
    """
    def __init__ (self, folder_address, cluster_name = None, identicals = [], best_image_name = None, matches = set(), nomatches = set()):
        self.address = folder_address
        if not cluster_name :
            self.name = folder_address.split("/")[-1]
        else:
            self.name = cluster_name
        image_files = sorted([f for f in os.listdir(self.address) if not f.startswith('.')])
        self.images_dict = {f: ImgObj(os.path.join(self.address, f), self.name) for f in image_files}
        self.images = list(self.images_dict.values())
        self.identicals = identicals #list of sets of image names
        self.number = len(self.images) #number of coins - default number of images

        if best_image_name:
            try:
                self.best_image = self.images_dict[best_image_name]
            except:
                print("WARNING: Can't find best image " + str(self.images_dict))
        else:
            if len(self.images) > 0:
                self.best_image = self.images[0] #default first image

        self.matches = matches #for adding right image name that belong to the cluster
        self.nomatches = nomatches #for adding right image name that does not belong to the cluster

    def get_best_image_index(self):
        best_image_name = self.best_image.name
        for index, obj in enumerate(self.images):
            if obj.name == best_image_name:
                return index

class Stage:
    """track progress in a stage
    name: "Validate Clusters", "Inspect Verified", "Verified vs Singles", "Singles vs Singles"
    """
    def __init__(self, stage_number, project_address):
        self.stages = ["Validate Clusters", "Inspect Verified", "Verified vs Singles", "Singles vs Singles"]
        self.stage_number = stage_number
        self.name = self.stages[self.stage_number]
        self.clusters_yet_to_check = set() #cluster names

        if stage_number == 0:
            #all images in clusters (not singles)
            cluster_folders = [f for f in os.listdir(project_address) if (not f.startswith('.')) and (not f.startswith("Singles")) and (not f.startswith("Verified"))]
            for cluster_name in cluster_folders:
                    self.clusters_yet_to_check.add(cluster_name.split('.')[0])

        elif stage_number == 1 or stage_number == 2:
            #all images in Verified represent their cluster
            verified_cluster_names = [f for f in os.listdir(project_address+"/Verified") if (not f.startswith('.'))]
            for cluster_name in verified_cluster_names:
                self.clusters_yet_to_check.add(cluster_name.split(".")[0])


        else:
            #all images in Singles are considered a single cluster
            single_names = [f for f in os.listdir(project_address+"/Singles") if (not f.startswith('.'))]
            for single_name in single_names:
                self.clusters_yet_to_check.add(single_name.split(".")[0])
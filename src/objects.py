import os
from collections import defaultdict
import math

class ImgObj:
    """Class object for an image
    Updated as changes happen
    """
    def __init__(self, name, cluster):
        self.name = name #with .jpg
        self.id = self.name.split(".")[0] #without .jpg
        try:
            self.suffix = self.name.split(".")[1]
        except:
            print(name)

        self.cluster = cluster

class Cluster:
    """Class object for a cluster of coins
    images, best_images : Updated dynamically
    name: updated upon saving
    number: updated upon saving
    """
    def __init__ (self, cluster_name = None, images=[], identicals = [], best_image_name = None, matches = set(), nomatches = set()):
        self.name = cluster_name
        self.images_dict = {f: ImgObj(f, cluster_name) for f in images}
        self.images = list(self.images_dict.values())
        self.identicals = identicals #list of sets of image names

        if best_image_name:
            self.best_image = self.images_dict[best_image_name]
        else:
            if len(self.images) > 0:
                self.best_image = self.images[0] #default first image
            else:
                self.best_image = None

        self.matches = matches #for adding right image name that belong to the cluster
        self.nomatches = nomatches #for adding right image name that does not belong to the cluster
        self.compared_before = set()

    def get_best_image_index(self):
        best_image_name = self.best_image.name
        for index, obj in enumerate(self.images):
            if obj.name == best_image_name:
                return index
class Stage:
    """track progress in a stage
    """
    def __init__(self, stage_number, project_data):
        stages = ["Validate Clusters", "Merge Clusters", "Clusters vs Singles", "Single vs Single", "Find Identicals"]
        self.stage_number = stage_number
        self.name = stages[self.stage_number]

        if stage_number < 3 :
            #all images in clusters (not singles)
            self.clusters_yet_to_check = {c for c in project_data["clusters"] if c != "Singles"}

        elif stage_number == 3:
            #all images in Singles are considered one cluster
            self.clusters_yet_to_check = {f for f in (project_data["clusters"]["Singles"]["original_images"] + project_data["clusters"]["Singles"]["matches"] )}

        else:
            self.clusters_yet_to_check = {c for c in project_data["clusters"]}
        #if A is compared with B => {A: {B}, B:{A}}
        self.past_comparisons = defaultdict(set)
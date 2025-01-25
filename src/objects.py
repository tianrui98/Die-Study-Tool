class ImgObj:
    """Class object for an image
    Updated as changes happen
    """
    def __init__(self, name, cluster):
        self.name = name #with .jpg
        self.id = self.name.split(".")[0] #without .jpg
        self.suffix = self.name.split(".")[1]
        self.cluster = cluster

class Cluster:
    """Class object for a cluster of coins
    images, best_images : Updated dynamically
    name: updated upon saving
    number: updated upon saving
    """
    def __init__ (self, cluster_name = None, images=[], identicals = [], best_image_name = None, matches = set(), nomatches = set(), bump_up_queue = []):
        self.name = cluster_name
        self.images_dict = {f: ImgObj(f, cluster_name) for f in images}
        
        # Fix: Preserve bump_up_queue order by handling it before sorting remaining images
        # First get images from bump_up_queue while preserving their order
        bumped_images = []
        for image_name in bump_up_queue:
            if image_name in self.images_dict:
                bumped_images.append(self.images_dict[image_name])
                
        # Then get remaining images sorted
        remaining_images = sorted([i for i in images if i not in bump_up_queue])
        remaining_image_objects = [self.images_dict[image_name] for image_name in remaining_images]
        
        # Combine bumped and remaining images
        self.images = bumped_images + remaining_image_objects

        self.identicals = identicals #list of sets of image names

        #move or set best image as the first image
        if best_image_name and best_image_name in self.images_dict:
            self.best_image = self.images_dict[best_image_name]
            self.images = [i for i in self.images if i.name != best_image_name] #move best image to the first position to be displayed on the left
            self.images.insert(0, self.best_image)

        elif best_image_name:
            self.images_dict[best_image_name]= ImgObj(best_image_name, cluster_name)
            self.images = [self.images_dict[best_image_name]] + self.images
            self.best_image = self.images[0]
        else:
            if len(self.images) > 0:
                self.best_image = self.images[0] #default best image is the first image in the list
            else:
                self.best_image = None
    
        self.matches = matches #for adding right image name that belong to the cluster
        self.nomatches = nomatches #for adding right image name that does not belong to the cluster
        self.compared_before = matches.union(nomatches)

    def get_best_image_index(self):
        best_image_name = self.best_image.name
        for index, obj in enumerate(self.images):
            if obj.name == best_image_name:
                return index

    def _get_image_index (self, image_name):
        for i in range(len(self.cluster.images)):
            im = self.cluster.images[i]
            if im.name == image_name:
                return i
class Stage:
    """track progress in a stage
    """
    def __init__(self, stage_number, project_data):
        stages = ["1. Correcting False Discovery Rate", #Confirm true clusters from the ML-created clusters. The rest unselected images will be thrown into "Singles"
                  "2. Correcting Sensitivity Rate", #Compare true clusters with each other and with singles (potential False Negatives) to merge true clusters
                  "3. Single vs Single", #Compare single with single to find remaining clusters or merge identicals 
                  "4. Find Identicals" #Mark out identical images so we don't double count
                  ]
        self.stage_number = stage_number
        self.name = stages[self.stage_number]

        if stage_number == 0 or stage_number == 1 :
            #all clusters (not singles)
            self.clusters_yet_to_check = {c for c in project_data["clusters"] if c != "Singles"}

        elif stage_number == 2:
            #all images in Singles are considered one cluster
            self.clusters_yet_to_check = {f for f in project_data["clusters"]["Singles"]["images"]}

        else:
            self.clusters_yet_to_check = {c for c in project_data["clusters"]}

        #if A is compared with B => {A: {B}, B:{A}}
        self.clusters_done = set()

        self.bump_up_queue =[]
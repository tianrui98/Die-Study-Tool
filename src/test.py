"""Test the correctedness of the program"""
from collections import defaultdict
import os

from sqlalchemy import all_
import src.progress as progress

class Test:

    def __init__ (self, singles = []):
        self.data = defaultdict(set)
        self.singles = set(singles)
        self.actions = {}
        self.past_comparisons = {}

    def fill_in_singles(self, clusters_data):
        self.singles = clusters_data["Singles"]["matches"]

    def record_action(self, left, right, action):
        self.actions[(left, right)] = action

    def clear_actions(self):
        self.past_comparisons.update(self.actions)
        self.actions = {}

    def clear_comparisons(self):
        self.past_comparisons = {}

    def translate_actions(self, stage_number):
        for (left, right) in self.actions:
            if self.actions[(left, right)] == "match":
                self.match(left,right, stage_number)
            else:
                self.unmatch(left,right, stage_number)

        self.move_singleton_to_singles()
        self.clear_actions()

    def move_singleton_to_singles(self):
        to_pop = []
        for left, matches in self.data.items():
            if len(matches) ==0:
                to_pop.append(left)
                self.singles.add(left)
        for left in to_pop:
            self.data.pop(left)

    def stage0_match(self, left, right):
        if left != right:
            self.data[left].add(right)

    def stage0_unmatch(self,left, right):
        self.data[left].add(right)
        self.data[left].remove(right)
        self.singles.add(right)

    def stage1_match(self,left,right):
        if right not in self.singles:
            self.data[left]= set.union(self.data[left], self.data[right])
            self.data.pop(right)
        else:
            self.singles.remove(right)
        self.data[left].add(right)

    def stage1_unmatch(self,left,right):
        pass

    def stage2_match(self,left,right):
        self.data[left].add(right)
        if left in self.singles:
            self.singles.remove(left)
        if right in self.singles:
            self.singles.remove(right)

    def stage2_unmatch(self,left,right):
        pass

    def match(self, left, right, stage_number):
        if stage_number == 0:
            self.stage0_match(left, right)
        elif stage_number == 1:
            self.stage1_match(left, right)
        elif stage_number == 2:
            self.stage2_match(left,right)

    def unmatch(self, left, right, stage_number):
        if stage_number == 0:
            self.stage0_unmatch(left, right)
        elif stage_number == 1:
            self.stage1_unmatch(left, right)
        elif stage_number == 2:
            self.stage2_unmatch(left,right)

    def swap_best_image(self, left,right):
        if left in self.data:
            self.data[right] = self.data[left]
            self.data.pop(left)

    def test_cluster_correctedness(self, clusters_data):
        if len(self.data) == 0:
            return None
        for c in clusters_data.keys():
            if c != "Singles":
                best_image_name = clusters_data[c]["best_image_name"]
                if best_image_name in self.data:
                    for match in clusters_data[c]["matches"]:
                        if match != best_image_name:
                            assert (match in self.data[best_image_name]), f"{match} in clusters_data {clusters_data[c]} but not in test"
                    for match in self.data[best_image_name]:
                        assert (match in clusters_data[c]["matches"]), f"{match} in test {self.data} but not in clusters_data {clusters_data[c]}"
        singles = set(clusters_data["Singles"]["matches"])
        assert singles == self.singles, f"singles in clusters_data {singles} don't share the same element with self.singles = {self.singles}"
        print("cluster correctness test passed")

    def test_image_number(self, clusters_data, project_address):
        """test if no. of images in clusters_data is the same as in test data
        """
        number_in_clusters = 0
        for c, cluster_info in clusters_data.items():
            if c != "Singles":
                #best image not in matches
                number_in_clusters += 1
            number_in_clusters += len(cluster_info["matches"])

        number_in_test = 0
        for _, matches in self.data.items():
            number_in_test += 1 + len(matches)
        number_in_test += len(self.singles)
        number_in_folder = len(os.listdir(project_address))
        assert number_in_clusters == number_in_test, f"number in cluster = {number_in_clusters} number in test = {number_in_test}"
        assert number_in_clusters == number_in_folder, f"number in cluster = {number_in_clusters} number in folder = {number_in_folder}"
        print("image number test passed")

    def test_export(self, clusters_data, project_address, destination_address):
        """Test if all clusters have corresponding folders and if total image number remains the same
        """
        items_in_destination = os.listdir(destination_address)
        folders_in_destination = [i for i in items_in_destination if not (("." in i) or ("Verified" in i))   ]

        for c, cluster_info in clusters_data.items():
            if c == "Singles":
                final_name = "Singles"
            else:
                final_name = progress._concatenate_image_names_in_data(cluster_info)
            assert final_name in items_in_destination, f"cluster {final_name} not in destination"
            for match in cluster_info["matches"]:
                assert match in os.listdir(os.path.join(destination_address, final_name )), f"{match} not in destination"

            if c != "Singles":
                best_image = cluster_info["best_image_name"]
                assert best_image in os.listdir(os.path.join(destination_address, final_name )), f"{best_image} not in destination"

        original_images = set([i for i in os.listdir(project_address) if not i.startswith('.')])
        destination_images = set()

        for folder in folders_in_destination:
            images = os.listdir(os.path.join(destination_address, folder))
            destination_images = destination_images.union(images)
            for im in images:
                assert im in original_images, f"{im} in destination but not in original folder"

        for im in original_images:
            assert im in destination_images, f"{im} in original but not in destination folder"

        print("export test passed.")

    def test_comparison (self, project_address, stage_number):
        """Check if every image has been compared with another/best_image
        """
        original_images =[i for i in os.listdir(project_address) if not i.startswith('.')]
        all_comparisons = { i for i in self.past_comparisons}
        best_image_dict = {}
        for left, matches in self.data.items():
            for im in matches:
                best_image_dict[im] = left
            best_image_dict[left] = left
        for im in self.singles:
            best_image_dict[im] = im

        print(best_image_dict)
        for i in range(len(original_images)):
            for j in range(i + 1, len(original_images)):
                a = original_images[i]
                b = original_images[j]

                if not ((a,b) in all_comparisons or (b,a) in all_comparisons):
                    if stage_number == 1:
                        a_best = best_image_dict[a]
                        b_best = best_image_dict[b]
                        assert ((a_best, b_best) in all_comparisons) or ((b_best, a_best) in all_comparisons), f"pair {(a,b)} not compared"


        print("comparison test passed.")
"""
progress_data follows json format. Only has strings, dictionaries, and lists.
"""
#todo First compare image 1 against all others. Second, remove all matched images from the pool of comparisons. Third, move to the next (remaining) coin and repeat
#todo Discovered a flaw in step 2: All coins are compared to each other more than once. It should rather work like this: Step1: A is compared to B, C, and D. Step2: B is compared to  C and D. Step 3: C is compared to D. This simple model assumes that they are no matches. If, however, B is merged with C, the comparisons would be over.

#todo if A is compared with B (regardless of match), A should not be compared with B again.

import json
import os
import shutil
import glob
import pandas as pd
from src.objects import *
from src.root_logger import *
from datetime import datetime
from collections import defaultdict
from pathlib import Path

def _serialize_identicals(identicals):
    res = []
    for s in identicals:
        res.append(list(s))
    return res

def _deserialize_identicals(identicals):
    res = []
    for l in identicals:
        res.append(set(l))
    return res

def _serialize_past_comparisons(past_comparisons):
    return {key : list(val) for key, val in past_comparisons.items() }

def _deserialize_past_comparisons(past_comparisons):
    d = {key : set(val) for key, val in past_comparisons.items() }
    return defaultdict(set, d)

def _collect_identicals(identicals):
    identical_group_list = []
    identical_name_list =[]
    for identical_set in sorted(identicals):
        identical_group_name = ""
        prev_type = ""
        for image_name in list(identical_set):
            image_id = image_name.split(".")[0] #without .jpg
            identical_name_list.append(image_id)
            if ";" in image_id:
                curr_type, curr_name = image_id.split(";")
            else:
                curr_type=""
                curr_name=image_id
            if curr_type != prev_type:
                identical_group_name += str("_" + image_id)
            else:
                identical_group_name += str("_" + curr_name)
            prev_type = curr_type
        if identical_group_name[0] == "_":
            identical_group_name = identical_group_name[1:]
        identical_group_list.append(identical_group_name)

    return identical_group_list, identical_name_list

def _concatenate_image_names(cluster):
    """get cluster name"""
    identical_group_list, identical_name_list = _collect_identicals(cluster.identicals)

    matches = []
    if cluster.best_image.id not in identical_name_list:
        matches.append(cluster.best_image.id)

    for image_name in sorted(cluster.matches):
        image_id = image_name.split(".")[0]
        if image_id not in identical_name_list:
            matches.append(image_id)

    final_names = identical_group_list + matches
    final_names = [n for n in final_names if not n == ""]
    new_cluster_name = "_".join(sorted(final_names))

    #max file name (255)
    if len(new_cluster_name) > 150:
        new_cluster_name = new_cluster_name[:147] + "_etc"
    return new_cluster_name

def _concatenate_image_names_in_data(cluster_info):
    identical_group_list, identical_name_list = _collect_identicals(cluster_info["identicals"])

    matches = []
    if cluster_info["best_image_name"].split(".")[0] not in identical_name_list:
        matches.append(cluster_info["best_image_name"].split(".")[0])

    for image_name in sorted(cluster_info["matches"]):
        image_id = image_name.split(".")[0]
        if image_id not in identical_name_list:
            matches.append(image_id)

    final_names = identical_group_list + matches
    final_names = [n for n in final_names if not n == ""]
    new_cluster_name = "_".join(sorted(final_names))

    #max file name (255)
    if len(new_cluster_name) > 150:
        new_cluster_name = new_cluster_name[:147] + "_etc"
    return new_cluster_name

def _change_name_in_past_comparisons (old_name, new_name, stage):
    if old_name in stage.past_comparisons:
        #change name in its counterpart's record
        for counterpart in stage.past_comparisons[old_name]:
            old_set = stage.past_comparisons.pop(counterpart)
            new_set = {e for e in old_set if e != old_name}
            new_set.add(new_name)
            stage.past_comparisons[counterpart] = new_set

        #change its own name
        old_set = stage.past_comparisons.pop(old_name)
        stage.past_comparisons[new_name] = old_set
    return stage

def _change_name_in_clusters_yet_to_check (old_name, new_name, stage):
    if old_name in stage.clusters_yet_to_check:
        stage.clusters_yet_to_check = {e for e in stage.clusters_yet_to_check if e != old_name}
        stage.clusters_yet_to_check.add(new_name)
    return stage

def _change_name_in_current_cluster(old_name, new_name, progress_data, project_name, stage):
    if str(stage.stage_number) in progress_data[project_name]["stages"] and old_name == progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"]:
        progress_data["current_cluster"] = new_name
    return progress_data

def start_new_project(original_project_address, project_name):
    """Create a new project. This will add a new hashmap to existing progress_data with the cluster information.
    The images with valid extensions under the original project folder will be copied into a new project folder within the program.
    All images under a cluster will be stored under "matches".
    Matches should include all images under the cluster, including the best image (by default the first image)

    Args:
        original_project_address (str): the address of the chosen project folder
        project_name (str): the project name

    Returns:
        str, hashmap: new_project_folder, progress_data
    """
    #copy all images in the original folder to a new folder
    new_project_address =os.path.join(os.getcwd() ,"projects", project_name)
    os.makedirs(new_project_address)

    for file_extension in ("*.jpg", "*.jpeg", "*.png"):
        for file_path in glob.glob(os.path.join(original_project_address, '**', file_extension), recursive=True):
            new_path = os.path.join(new_project_address, os.path.basename(file_path))
            shutil.copy(file_path, new_path)

    #read existing progress data
    data_file = open("data.json", "r")
    progress_data = json.loads(data_file.read())
    progress_data[project_name] = {"clusters": {}, "stages": {}}

    #populate "cluster" with cluster information based on original project folders
    for cluster_name in os.listdir(original_project_address):
        if not cluster_name.startswith('.'):
            original_images = sorted([f for f in os.listdir(os.path.join(original_project_address, cluster_name)) if not f.startswith(".")])
            progress_data[project_name]["clusters"][cluster_name] = {
                "matches": original_images[1:],
                "nomatches":[],
                "identicals":[],
                "best_image_name": original_images[0]}

    return new_project_address , progress_data

def create_new_stage_in_progress_data(progress_data, project_name, stage):
    progress_data[project_name]["stages"][str(stage.stage_number)] ={
        "clusters_yet_to_check": list(stage.clusters_yet_to_check)
        }
    return progress_data


def _create_cluster_info_dict (cluster):
    dict =  {
    "images": [f.name for f in cluster.images],
    "identicals": _serialize_identicals(cluster.identicals),
    "matches": list(cluster.matches),
    "nomatches": list(cluster.nomatches),
    "best_image_name": cluster.best_image.name
    }
    return dict

def _merge_singles(cluster, clusters_data, old_cluster_name):
    """
    In stage 2, the Singles that are matched to the current cluster will be taken out of the Singles cluster

    Args:
        cluster ([type]): [description]
        clusters_data ([type]): [description]
        new_cluster_name ([type]): [description]

    Returns:
        [type]: [description]
    """
    new_cluster_name = old_cluster_name.split('.')[0]
    images_in_singles = set(clusters_data["Singles"]["best_image_name"] + clusters_data["Singles"]["matches"])
    for matched_single_name in cluster.matches:
        if matched_single_name in images_in_singles:
            images_in_singles.remove(matched_single_name)
        new_cluster_name += "_" + matched_single_name.split(".")[0]
    #remove the left image from "Singles" if it has been matched to another single
    if len(cluster.matches) >0 and cluster.name in images_in_singles:
        images_in_singles.remove(cluster.name)
        new_cluster_name += "_" + cluster.name.split(".")[0]
    if len(new_cluster_name) > 150:
        new_cluster_name = new_cluster_name[:147] + "_etc"
    clusters_data["Singles"]["matches"] = list(images_in_singles)
    return clusters_data, new_cluster_name

def save_progress_data_midway(project_name, stage,cluster, progress_data):
    """Save progress without changing cluster names or creating new clusters
    """
    if str(stage.stage_number) not in progress_data[project_name]["stages"]:
        progress_data = create_new_stage_in_progress_data(progress_data, project_name, stage)

    clusters_data = progress_data[project_name]["clusters"]
    #if Cluster is None (end of project) then do nothing
    if not cluster:
        return
    clusters_data[cluster.name] = _create_cluster_info_dict(cluster)

    progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"] = cluster.name
    #update clusters_yet_to_check
    progress_data[project_name]["stages"][str(stage.stage_number)]["clusters_yet_to_check"] = list(stage.clusters_yet_to_check)
    #update past_comparisons
    progress_data[project_name]["stages"][str(stage.stage_number)]["past_comparisons"] = _serialize_past_comparisons(stage.past_comparisons)

    #write new clusters_data
    progress_data[project_name]["clusters"] = clusters_data

    data_file = open("data.json", "w")
    json.dump(progress_data, data_file)
    data_file.close()

    return progress_data, stage

def save_progress_data(project_name, stage, cluster, progress_data):
    """
    Make changes to the progress data
    {"project_name" : {  "clusters": {cluster_name: {
                                                        "images": []
                                                        "identicals": [],
                                                        "matches": [],
                                                        "nomatches": []:
                                                        "best_image_name": "" :
                                                    }
                                            }
                            "stages": { 0: {
                                        "current_cluster" : ,
                                        "clusters_yet_to_check": [],
                                        "past_comparisons": {img_name : []} }}
    }

    *the update on "clusters" will only happen for stage 0, 3 and 4
    Return: progress_data, stage
    """
    if str(stage.stage_number) not in progress_data[project_name]["stages"]:
        progress_data = create_new_stage_in_progress_data(progress_data, project_name, stage)

    clusters_data = progress_data[project_name]["clusters"]
    #if Cluster is None (end of project) then do nothing
    if cluster:
        old_cluster_name = cluster.name
        new_cluster_name = None
        if stage.stage_number == 0:
            #move nomatches to singles cluster
            for image_name in list(cluster.nomatches):
                clusters_data["Singles"]["matches"].append(image_name)
            # if all images do not belong to the cluster -> delete the cluster
            if len(cluster.matches) == 0 and len(cluster.nomatches) > 0:
                best_image_name = cluster.best_image.name
                clusters_data["Singles"]["matches"].append(best_image_name)
                clusters_data.pop(old_cluster_name)
            else:
                #delete old cluster name
                new_cluster_name = _concatenate_image_names(cluster)
                clusters_data.pop(old_cluster_name)
                clusters_data[new_cluster_name] = _create_cluster_info_dict(cluster)

        elif stage.stage_number == 1:
            best_image_cluster_dict = _create_best_image_cluster_dict(clusters_data)
            #merge matched cluster with current cluster
            new_cluster_name = old_cluster_name
            for matched_best_image_name in list(cluster.matches):
                #the case for cluster vs cluster
                if matched_best_image_name in best_image_cluster_dict:
                    matched_cluster_name = best_image_cluster_dict[matched_best_image_name]
                    #transfer all images under matched cluster to the current cluster
                    clusters_data[old_cluster_name]["matches"].extend(
                        clusters_data[matched_cluster_name]["matches"])
                    clusters_data[old_cluster_name]["matches"].append(matched_best_image_name)
                    _ = clusters_data.pop(matched_cluster_name)
                    new_cluster_name += "_" + matched_cluster_name
                #the case for cluster vs single
                else:
                    single_name = matched_best_image_name
                    clusters_data[old_cluster_name]["matches"].append(single_name)
                    clusters_data["Singles"]["matches"].remove(single_name)
                    new_cluster_name += "_" + matched_best_image_name.split('.')[0]
            if len(new_cluster_name) > 150:
                new_cluster_name = new_cluster_name[:147] + "_etc"
            clusters_data[new_cluster_name] = clusters_data.pop(old_cluster_name)

        elif stage.stage_number == 2:
            clusters_data, new_cluster_name = _merge_singles(cluster, clusters_data, old_cluster_name)
            #create new cluster from matched singles
            if len(cluster.matches) > 0:
                clusters_data[new_cluster_name] = {
                    "images": [],
                    "identicals": [],
                    "matches": list(cluster.matches),
                    "nomatches": [],
                    "best_image_name": cluster.best_image.name
                }

        elif stage.stage_number == 3:
            #overwrite only the identicals info
            clusters_data[cluster.name]["identicals"] = _serialize_identicals(cluster.identicals)

        if new_cluster_name:
            stage = _change_name_in_clusters_yet_to_check(old_cluster_name, new_cluster_name, stage)
            stage = _change_name_in_past_comparisons(old_cluster_name, new_cluster_name, stage)
            #update current cluster
            progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"] = new_cluster_name
        else:
            progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"] = old_cluster_name
        #update clusters_yet_to_check
        progress_data[project_name]["stages"][str(stage.stage_number)]["clusters_yet_to_check"] = list(stage.clusters_yet_to_check)
        #update past_comparisons
        progress_data[project_name]["stages"][str(stage.stage_number)]["past_comparisons"] = _serialize_past_comparisons(stage.past_comparisons)

    #write new clusters_data
    progress_data[project_name]["clusters"] = clusters_data

    #delete previous stage info to reduce memory
    for i in range(stage.stage_number):
        if str(i) in progress_data[project_name]["stages"]:
            _ = progress_data[project_name]["stages"].pop(str(i))

    data_file = open("data.json", "w")
    json.dump(progress_data, data_file)
    data_file.close()

    return progress_data, stage

def clear_current_project(project_name, progress_data):
    """remove current project from progress data & delete project folder
    """
    if project_name in progress_data:
        _ = progress_data.pop(project_name)
    data_file = open("data.json", "w")
    json.dump(progress_data, data_file)
    data_file.close()
    project_folder = os.path.join(os.getcwd() ,"projects", project_name)
    shutil.rmtree(project_folder)

def checkout_progress():
    """read json into dictionary
    """
    data_file = open("data.json", "r")
    progress_data = json.loads(data_file.read())
    return progress_data

def load_progress(project_name, create_next_cluster = True, data_address = "data.json"):
    """read progress data and create objects"""
    app_folder = str(Path(__file__).resolve().parent.parent)
    if app_folder not in data_address:
        data_address_full = os.path.join(app_folder, data_address)
    else:
        data_address_full = data_address

    data_file = open(data_address_full, "r")
    progress_data = json.loads(data_file.read())
    #retrieve latest stage
    stage_number= max(progress_data[project_name]["stages"].keys())
    stage_info = progress_data[project_name]["stages"][stage_number]
    stage = Stage(int(stage_number), progress_data[project_name])
    stage.clusters_yet_to_check = set(stage_info["clusters_yet_to_check"])
    stage.past_comparisons= _deserialize_past_comparisons(stage_info["past_comparisons"])
    #retrieve latest cluster
    current_cluster = stage_info["current_cluster"]

    if stage_number == "0":
        cluster_info = progress_data[project_name]["clusters"][current_cluster]
        cluster = Cluster( cluster_name = current_cluster,
            images = cluster_info["images"],
            identicals = _deserialize_identicals(cluster_info["identicals"]),
            best_image_name = cluster_info["best_image_name"],
            matches = set(cluster_info["matches"]),
            nomatches = set(cluster_info["nomatches"]))
    else:
        if current_cluster in stage.clusters_yet_to_check:
            cluster = _create_a_cluster(stage, progress_data[project_name]["clusters"],current_cluster)
        # if current cluster has already been checked. give the next cluster in line
        else:
            next_in_line = sorted(list(stage.clusters_yet_to_check), key= lambda s: s.split("_")[0])[0]
            cluster = _create_a_cluster(stage, progress_data[project_name]["clusters"], next_in_line)
            progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"] = cluster.name

    return progress_data, stage, cluster

def check_cluster_completion(cluster,stage):
    """Check if all images in the current cluster have all been processed
    """
    if not cluster:
        return True
    all_compared_already = all([imgObj.name in stage.past_comparisons[cluster.best_image.name] for imgObj in cluster.images if imgObj.name != cluster.best_image.name ])
    return all_compared_already or (len(cluster.matches) + len(cluster.nomatches) + len(cluster.compared_before) >= len(cluster.images) - 1)


def check_stage_completion(stage, clusters_data):
    if stage.stage_number == 1:
        if (len(stage.clusters_yet_to_check) == 0) :
            return True
        elif (len(stage.clusters_yet_to_check) == 1 and len(clusters_data["Singles"]["matches"]) == 0):
            logger.debug(f"Skip cluster {stage.clusters_yet_to_check[0]}")
            return True
    elif stage.stage_number == 2:
        if (len(stage.clusters_yet_to_check) == 0):
            return True
        elif (len(clusters_data["Singles"]["matches"]) <= 1):
            remaining_single = clusters_data["Singles"]["matches"]
            logger.debug(f"Skip single {remaining_single}")
            return True
    else:
        return len(stage.clusters_yet_to_check) == 0
    
    return False

def check_project_completion(stage, clusters_data):
    return check_stage_completion(stage, clusters_data) and stage.stage_number == 3


def check_part1_completion(cluster,stage, clusters_data):
    stage_completed = check_stage_completion(stage, clusters_data)
    is_second_stage = stage.stage_number == 2
    case1 = stage_completed and is_second_stage

    #we are at stage 1 and we don't have any Single or cluster to compare with the last cluster
    case2 = stage.stage_number == 1 and check_cluster_completion(cluster, stage) and len(stage.clusters_yet_to_check) == 1\
    and len(set(clusters_data["Singles"]["matches"]).intersection(cluster.nomatches)) == len(clusters_data["Singles"]["matches"])

    return case1 or case2

def mark_compared(left_name, right_name, stage):
    stage.past_comparisons[left_name].add(right_name)
    stage.past_comparisons[right_name].add(left_name)

    return stage

def unmark_compared(left_name, right_name, stage):
    stage.past_comparisons[left_name].remove(right_name)
    stage.past_comparisons[right_name].remove(left_name)
    return stage

def mark_cluster_completed(cluster, stage, clusters_data):
    """Remove current cluster name from clusters_yet_to_check. Before updating cluster name"""

    if cluster.name in stage.clusters_yet_to_check:
        stage.clusters_yet_to_check.remove(cluster.name)

    #Inspect Verified Stage and the rest: move the matched clusters off the yet_to_check list
    if stage.stage_number > 0 and stage.stage_number < 3:
        best_image_cluster_dict = _create_best_image_cluster_dict(clusters_data)
        for image_name in cluster.matches:
            stage = mark_compared(cluster.best_image.name, image_name,stage)
            if stage.stage_number == 1 and image_name in best_image_cluster_dict:
                    matched_cluster_name = best_image_cluster_dict[image_name]
            else:
                matched_cluster_name = image_name
            if matched_cluster_name in stage.clusters_yet_to_check:
                stage.clusters_yet_to_check.remove(matched_cluster_name)
        for image_name in cluster.nomatches:
            stage = mark_compared(cluster.best_image.name, image_name,stage)

    return stage

def unmark_cluster_completed(cluster,stage, clusters_data):
    """reverse marking cluster completed"""

    if cluster.name not in stage.clusters_yet_to_check:
        stage.clusters_yet_to_check.add(cluster.name)

    #Inspect Verified Stage and the rest: move the matched clusters off the yet_to_check list
    if stage.stage_number > 0 and stage.stage_number < 4:
        best_image_cluster_dict = _create_best_image_cluster_dict(clusters_data)
        for image_name in list(cluster.matches):
            stage = unmark_compared(cluster.best_image.name, image_name,stage)
            if stage.stage_number == 1 and image_name in best_image_cluster_dict:
                matched_cluster_name = best_image_cluster_dict[image_name]
            else:
                matched_cluster_name = image_name
            if matched_cluster_name not in stage.clusters_yet_to_check:
                stage.clusters_yet_to_check.add(matched_cluster_name)
        for image_name in cluster.nomatches:
            stage = unmark_compared(cluster.best_image.name, image_name,stage)

    return stage

def copy_best_image_to_verified(cluster, project_name):
    project_folder = os.path.join(os.getcwd() ,"projects", project_name)
    if not os.path.exists(os.path.join(project_folder, "Verified")):
        os.mkdir(os.path.join(project_folder, "Verified"))
    old_image_address = os.path.join(cluster.address, cluster.best_image.name)
    new_image_address = os.path.join(project_folder, "Verified", cluster.name + ".jpg")
    shutil.copyfile(old_image_address, new_image_address)
    return cluster


def _create_a_cluster(stage, clusters_data, next_cluster_name):
    if stage.stage_number == 0 :
        next_cluster = Cluster(cluster_name = next_cluster_name, images = clusters_data[next_cluster_name]["matches"] + [clusters_data[next_cluster_name]["best_image_name"]], identicals = [], best_image_name = None, matches = set(), nomatches = set())

    elif stage.stage_number == 1:
        best_image_cluster_dict = {v["best_image_name"]: k for k, v in clusters_data.items() if not k == "Singles"}
        next_cluster = Cluster(cluster_name = next_cluster_name, images = [i for i in best_image_cluster_dict] + list(clusters_data["Singles"]["best_image_name"] + clusters_data["Singles"]["matches"]), identicals = [], best_image_name = clusters_data[next_cluster_name]["best_image_name"], matches = set(), nomatches = set())

        #replace the image's cluster name with the cluster it represents
        for image_name, image_object in next_cluster.images_dict.items():
            if image_name in best_image_cluster_dict:
                image_object.cluster = best_image_cluster_dict[image_name]
            else:
                image_object.cluster = "Singles"
            next_cluster.images_dict[image_name] = image_object

    elif stage.stage_number == 2:
        #A cluster should include all images in the Singles folder, except those have been matched
        images = clusters_data["Singles"]["matches"]
        next_cluster = Cluster(cluster_name = next_cluster_name, images = images, identicals = [], best_image_name = next_cluster_name, matches = set(), nomatches = set())
        #replace the image's cluster name with the cluster it represents
        for image_name, image_object in next_cluster.images_dict.items():
            image_object.cluster = "Singles"
            next_cluster.images_dict[image_name] = image_object
    else:
        if next_cluster_name != "Singles":
            images = clusters_data[next_cluster_name]["matches"] + [clusters_data[next_cluster_name]["best_image_name"]]
        else:
            images = clusters_data[next_cluster_name]["matches"]
        next_cluster = Cluster(cluster_name = next_cluster_name, images = images,identicals = [], best_image_name = None, matches = set(), nomatches = set())
        #at stage 4, all images in the cluster folder have been marked as matches
        next_cluster.matches = {obj.name for obj in next_cluster.images[1:]}

    return next_cluster

def create_next_cluster(stage, clusters_data):
    """If the new cluster has only 1 image. the interface will take care of it"""
    if len(stage.clusters_yet_to_check) == 0:
        logger.debug(f"stage {stage.stage_number} clusters yet to check is zero")
        return None
    next_cluster_name = sorted(list(stage.clusters_yet_to_check),key= lambda s: s.split("_")[0])[0]
    next_cluster = _create_a_cluster(stage, clusters_data, next_cluster_name)
    return next_cluster


def create_next_stage( stage, project_data):
    new_stage = Stage(stage.stage_number+1, project_data)
    logger.debug(f"Next stage {new_stage.name}. yet to check: {new_stage.clusters_yet_to_check}")
    new_cluster = create_next_cluster(new_stage, project_data["clusters"])

    return new_cluster, new_stage

def create_find_identical_stage(project_data):
    new_stage = Stage(3, project_data)
    logger.debug(f"Next stage {new_stage.name}. yet to check: {new_stage.clusters_yet_to_check}")
    new_cluster = create_next_cluster(new_stage,project_data["clusters"])

    return new_cluster, new_stage

def _concatenate_identical_set(identical_set):
    identical_group_name = ""
    prev_type = ""

    for image_name in sorted(identical_set):
        image_id = image_name.split(".")[0] #without .jpg
        if ";" in image_id:
            curr_type, curr_name = image_id.split(";")
        else:
            curr_type = ""
            curr_name = image_id
        if curr_type != prev_type:
            identical_group_name += str("_" + image_id)
        else:
            identical_group_name += str("_" + curr_name)
        prev_type = curr_type
    
    if identical_group_name[0] == "_":
        identical_group_name = identical_group_name[1:]
    return "(" + identical_group_name +")"

def _concatenate_identicals(identicals):
    final_name = ""
    number_to_deduct = 0
    for identical_set in sorted(identicals):
        final_name += _concatenate_identical_set(identical_set)
        number_to_deduct += len(identical_set) - 1
    return final_name, number_to_deduct


def _create_cluster_folders(project_name, clusters_data, dest_folder):
    project_folder = os.path.join(os.getcwd() ,"projects", project_name)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    dest_verified_folder = os.path.join(dest_folder, "Verified")
    if not os.path.exists(dest_verified_folder):
        os.makedirs(dest_verified_folder)

    for cluster_name, cluster_info in clusters_data.items():
        if cluster_name != "Singles":
            final_cluster_name = _concatenate_image_names_in_data(cluster_info)
        else:
            final_cluster_name = "Singles"
        dest_cluster_folder = os.path.join(dest_folder, final_cluster_name)
        if not os.path.exists(dest_cluster_folder):
            os.makedirs(dest_cluster_folder)
        for image_name in cluster_info["matches"]:
            shutil.copy(os.path.join(project_folder, image_name), os.path.join(dest_cluster_folder, image_name))

        if cluster_name != "Singles":
            if len(cluster_info["best_image_name"]) > 0 and cluster_info["best_image_name"] not in cluster_info["matches"]:
                shutil.copy(os.path.join(project_folder, cluster_info["best_image_name"]), os.path.join(dest_cluster_folder, cluster_info["best_image_name"]))
                #copy best image to verified
            shutil.copy(os.path.join(project_folder, cluster_info["best_image_name"]),os.path.join(dest_verified_folder, final_cluster_name + '.' + cluster_info["best_image_name"].split(".")[-1]))

def export_results(project_name, progress_data, save_address, keep_progress):
    """Generate excel sheet & move cluster out & wipe out progress data"""

    #write none-single clusters
    clusters = progress_data[project_name]["clusters"]
    max_length = 0
    total_number = 0
    for cluster_name, cluster in clusters.items():
        if cluster_name != "Singles":
            max_length = max(max_length, 1 + len(cluster["matches"]))

    columns = list(range(1, max_length + 1)) + ["Identical", "Num"]
    data = []
    for cluster_name, cluster in clusters.items():
        if cluster_name != "Singles":
            all_images = cluster["matches"] + [cluster["best_image_name"]]
            all_images = sorted(list(all_images))
            data_row = all_images + [""] * (max_length - len(all_images))
            identicals = cluster["identicals"]
            final_name, number_to_deduct = _concatenate_identicals(identicals)
            data_row.append(final_name)
            data_row.append(str(len(all_images) - number_to_deduct))
            total_number += len(all_images) - number_to_deduct
            data.append(data_row)

    #reorder clusters in ascending order
    data = sorted(data)
    # data = sorted(data, key = lambda row: (row[0], row[1]))
    #write "Singles" cluster
    all_singles =  progress_data[project_name]["clusters"]["Singles"]["matches"]
    identicals = progress_data[project_name]["clusters"]["Singles"]["identicals"]
    singles_seen = set()
    for identical_set in identicals:
        all_images = sorted(list(identical_set))
        data_row = all_images + [""] * (max_length - len(all_images))
        identical_final_name = _concatenate_identical_set(identical_set)
        data_row.append(identical_final_name)
        data_row.append("1")
        total_number += 1
        data.append(data_row)
        singles_seen = set.union(singles_seen, identical_set)

    for single_jpg in all_singles:
        single_id = single_jpg.split(".")[0]
        if single_jpg not in singles_seen:
            data_row = [single_id] + [""] * (max_length - 1)
            data_row.append("")
            data_row.append(str(1))
            data.append(data_row)
            total_number += 1

    data.append([""] * max_length +["sum"] + [str(total_number)])
    res = pd.DataFrame(data, columns=columns)
    res = res.applymap(lambda x : x.split('.')[0])

    project_folder = os.path.join(os.getcwd() ,"projects", project_name)
    project_folder_name = os.path.basename(project_folder) + "_" + str(datetime.now().strftime('%Y-%m-%d-%H-%M'))

    dest_folder = os.path.join(save_address, project_folder_name)

    _create_cluster_folders(project_name, progress_data[project_name]["clusters"], dest_folder)
    res.to_excel( os.path.join(dest_folder, "results_" + project_folder_name + ".xlsx"), index= False)

    return res, dest_folder

def _create_best_image_cluster_dict (clusters_data):
    return {v["best_image_name"]: k for k, v in clusters_data.items() if not k == "Singles"}

def create_new_objects(cluster, stage, project_name, progress_data, completion_status):
    """
    Creates new stage and cluster objects
    completion_status:
    - "project" : project complete
    - "part1": part1 complete
    - "stage": stage complete
    - "cluster": cluster complete
    """
    if completion_status == "project":
        return None, stage
    elif completion_status == "part1":
        return create_find_identical_stage(progress_data[project_name])
    elif completion_status == "stage":
            new_cluster, new_stage = create_next_stage(stage, progress_data[project_name])
            while ((not new_cluster) or check_stage_completion(new_stage, progress_data[project_name]["clusters"])):
                logger.debug(f"Skip stage {new_stage.name}")
                new_cluster, new_stage = create_next_stage(new_stage,progress_data[project_name])
            return new_cluster, new_stage
    else:
        clusters_data = progress_data[project_name]["clusters"]
        new_cluster = create_next_cluster(stage, clusters_data)

        #If the new cluster is already completed: skip
        if stage.stage_number < 3:
            while check_cluster_completion(new_cluster, stage):
                logger.debug(f"[create_new_objects] Skip cluster {new_cluster.name}")
                stage = mark_cluster_completed(new_cluster, stage,progress_data[project_name]["clusters"])
                if check_stage_completion(stage,progress_data[project_name]["clusters"]):
                    if check_project_completion(stage, progress_data[project_name]["clusters"]):
                        return None, stage
                    else:
                        return create_new_objects(new_cluster, stage, project_name, progress_data, "stage")
                else:
                    return create_new_objects(new_cluster, stage, project_name, progress_data, "cluster")
        return new_cluster, stage

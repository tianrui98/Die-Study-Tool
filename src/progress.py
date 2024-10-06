"""
progress_data follows json format. Only has strings, dictionaries, and lists.
"""

import json
import os
import shutil
import glob
import pandas as pd
from src.objects import *
from src.root_logger import *
from datetime import datetime
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

def _concatenate_image_names_from_list(image_list):
    matches = []
    for image_name in sorted(image_list):
        image_id = image_name.split(".")[0]
        matches.append(image_id)
    matches = [n for n in matches if not n == ""]
    new_cluster_name = "_".join(sorted(matches))

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


def _change_name_in_clusters_yet_to_check (old_name, new_name, stage):
    if old_name in stage.clusters_yet_to_check:
        stage.clusters_yet_to_check = {e for e in stage.clusters_yet_to_check if e != old_name}
        stage.clusters_yet_to_check.add(new_name)
    return stage

def  _change_name_in_clusters_done(old_name, new_name, stage):
    if old_name in stage.clusters_done:
        stage.clusters_done= {e for e in stage.clusters_done if e != old_name}
        stage.clusters_done.add(new_name)
    return stage


def _change_name_in_current_cluster(old_name, new_name, progress_data, project_name, stage):
    if str(stage.stage_number) in progress_data[project_name]["stages"] and old_name == progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"]:
        progress_data["current_cluster"] = new_name
    return progress_data

def start_new_project(original_project_address, project_name):
    """Create a new project. This will add a new hashmap to existing progress_data with the cluster information.
    The images with valid extensions under the original project folder will be copied into a new project folder within the program.
    All images under a cluster except the best image(by default the first image) will be stored under "matches".

    Args:
        original_project_address (str): the address of the chosen project folder
        project_name (str): the project name

    Returns:
        str, hashmap: new_project_folder, progress_data
    """
    #copy all images in the original folder to a new folder
    new_project_address =os.path.join(os.getcwd() ,"projects", project_name)
    os.makedirs(new_project_address)

    for file_extension in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
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
            if cluster_name == "Singles":
                best_image = ""
            else:
                best_image = original_images[0]
            
            progress_data[project_name]["clusters"][cluster_name] = {
                "images": original_images,
                "matches": [],
                "nomatches":[],
                "identicals":[],
                "best_image_name": best_image}
    logger.info(f"Start new project {project_name}")
    return new_project_address , progress_data

def create_new_stage_in_progress_data(progress_data, project_name, stage):
    progress_data[project_name]["stages"][str(stage.stage_number)] ={
        "current_cluster" :{
                                                                        "name":"",
                                                                        "unprocessed_matches":[],
                                                                        "unprocessed_nomatches":[],
                                                                        "unprocessed_marked_coin_group_list": []
                                                                        },
        "clusters_yet_to_check": list(stage.clusters_yet_to_check),
        "clusters_done":[]
        }
    return progress_data


def _create_cluster_info_dict (cluster):
    dict =  {
    "identicals": _serialize_identicals(cluster.identicals),
    "matches": list(cluster.matches),
    "nomatches": list(cluster.nomatches),
    "best_image_name": cluster.best_image.name,
    "images": [obj.name for obj in cluster.images]
    }
    return dict

def _merge_singles(cluster, clusters_data, old_cluster_name):
    """
    Args:
        cluster ([type]): [description]
        clusters_data ([type]): [description]
        old_cluster_name ([type]): name of the single being compared to other singles

    Returns:
        [type]: [description]
    """
    new_cluster_name = old_cluster_name.split('.')[0]
    images_in_singles = set(clusters_data["Singles"]["images"])
    for matched_single_name in cluster.matches:
        if matched_single_name in images_in_singles:
            images_in_singles.remove(matched_single_name)
        new_cluster_name += "_" + matched_single_name.split(".")[0]
    #remove the left image from "Singles" if it has been matched to another single
    if len(cluster.matches) >0 and cluster.name in images_in_singles:
        images_in_singles.remove(cluster.name)
    if len(new_cluster_name) > 150:
        new_cluster_name = new_cluster_name[:147] + "_etc"
    clusters_data["Singles"]["images"] = list(images_in_singles)
    return clusters_data, new_cluster_name

def write_progress_data_to_json(progress_data):
    data_file = open("data.json", "w")
    json.dump(progress_data, data_file, indent = 4)
    data_file.close()

def save_progress_data_midway(project_name, stage,cluster, progress_data, marked_coin_group_list):
    """Save progress and write to json without touching clusters_data
    """
    if str(stage.stage_number) not in progress_data[project_name]["stages"]:
        progress_data = create_new_stage_in_progress_data(progress_data, project_name, stage)

    #if Cluster is None (end of project) then do nothing
    if not cluster:
        return
    
    if marked_coin_group_list:
        unprocessed_marked_coin_group_list = marked_coin_group_list
    else:
        unprocessed_marked_coin_group_list = []
    #do not update cluster for single vs single because cluster name is single name
    if stage.stage_number == 0 or stage.stage_number == 3:
        progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"] = {
                                                                        "name":cluster.name,
                                                                        "unprocessed_matches":[],
                                                                        "unprocessed_nomatches":[],
                                                                        "unprocessed_marked_coin_group_list": unprocessed_marked_coin_group_list
                                                                        }
    else:
        progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"] = {
                                                                        "name":cluster.name,
                                                                        "unprocessed_matches":list(cluster.matches),
                                                                        "unprocessed_nomatches":list(cluster.nomatches),
                                                                        "unprocessed_marked_coin_group_list": unprocessed_marked_coin_group_list
                                                                        }

    #update stage properties
    progress_data[project_name]["stages"][str(stage.stage_number)]["clusters_yet_to_check"] = list(stage.clusters_yet_to_check)
    progress_data[project_name]["stages"][str(stage.stage_number)]["clusters_done"] = list(stage.clusters_done)

    #write new clusters_data

    write_progress_data_to_json(progress_data)

    return progress_data, stage

def stage0_consolidate_match_groups(cluster,marked_coin_group_list, clusters_data):
    """
    Update "clusters". Take unmatched images to "Singles". Create new cluster groups for matched coins.
    Update current cluster name if necessary.
    """
    
    if marked_coin_group_list == None:
        return clusters_data
    original_images_set = set(cluster.images_dict.keys())
    seen_images_set = set()
    old_cluster_name = cluster.name
    new_cluster_name = old_cluster_name
    new_cluster_name_list = []

    if len(marked_coin_group_list) <= 0:
        for image_name in original_images_set:
            clusters_data["Singles"]["images"].append(image_name)
        clusters_data.pop(old_cluster_name)
        return clusters_data
    else:
        for (matched_coin_list, best_image_name) in marked_coin_group_list:
            new_cluster_name = _concatenate_image_names_from_list(matched_coin_list)
            new_cluster_name_list.append(new_cluster_name)
            clusters_data[new_cluster_name] = {}

            clusters_data[new_cluster_name]["matches"] = []
            for image_name in matched_coin_list:
                if image_name != best_image_name:
                    clusters_data[new_cluster_name]["matches"].append(image_name)
                else:
                    clusters_data[new_cluster_name]["best_image_name"] = best_image_name
            
            nomatches = original_images_set - set(matched_coin_list) #mark all the other images in the original cluster as nomatches
            clusters_data[new_cluster_name]["nomatches"] = list(nomatches)
            clusters_data[new_cluster_name]["images"] = clusters_data[new_cluster_name]["matches"] + clusters_data[new_cluster_name]["nomatches"] + [clusters_data[new_cluster_name]["best_image_name"]]
            clusters_data[new_cluster_name]["identicals"] = []

            seen_images_set = seen_images_set.union(set(matched_coin_list))

    if old_cluster_name != new_cluster_name:
        #The old cluster has been broken up. 
        clusters_data.pop(old_cluster_name)
    #send the unmatched images to Singles
    single_images_list = list(original_images_set - seen_images_set)
    for image_name in single_images_list:
        clusters_data["Singles"]["images"].append(image_name)
    return clusters_data

def update_current_cluster(project_name, stage, progress_data, current_cluster_name, write_to_json = False):
    """
    Triggered after new objects are created. Update the current cluster in progress data
    """
    if str(stage.stage_number) not in progress_data[project_name]["stages"]:
        progress_data = create_new_stage_in_progress_data(progress_data, project_name, stage)

    progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"] = {
                                                                "name": current_cluster_name,
                                                                "unprocessed_matches":[],
                                                                "unprocessed_nomatches":[],
                                                                "unprocessed_marked_coin_group_list": []
                                                                }
    if write_to_json:
        write_progress_data_to_json(progress_data)
    
    return progress_data
   

def update_progress_data(project_name, stage, cluster, progress_data, marked_coin_group_list = None, write_to_json = False):
    """
    This will only be triggered when a cluster is deemed complete by the program.
    Make changes to the progress data. Modifies "clusters". By default will not write to json.
    {"project_name" : {  "clusters": {cluster_name: {
                                                        "identicals": [],
                                                        "matches": [],
                                                        "nomatches": [],
                                                        "best_image_name": "",
                                                        "images": []
                                                    }
                                            }
                            "stages": { "0": {
                                        "current_cluster" {"name":,
                                                            "unprocessed_matches":[],
                                                            "unprocessed_nomatches":[],
                                                            "unprocessed_marked_coin_group_list": []
                                                            }: ,
                                        "clusters_yet_to_check": [],
                                        "clusters_done":[]
                                         }}
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
            clusters_data = stage0_consolidate_match_groups(cluster,marked_coin_group_list, clusters_data)

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
                    clusters_data["Singles"]["images"].remove(single_name)
                    new_cluster_name += "_" + matched_best_image_name.split('.')[0]
            if len(new_cluster_name) > 150:
                new_cluster_name = new_cluster_name[:147] + "_etc"
            clusters_data[new_cluster_name] = clusters_data.pop(old_cluster_name)

        elif stage.stage_number == 2:
            if len(cluster.matches) > 0:
                clusters_data, new_cluster_name = _merge_singles(cluster, clusters_data, old_cluster_name)
                #create new cluster from matched singles
                clusters_data[new_cluster_name] = {
                    "identicals": [],
                    "matches": list(cluster.matches),
                    "nomatches": [],
                    "best_image_name": cluster.best_image.name,
                    "images": [obj.name for obj in cluster.images]
                }

        elif stage.stage_number == 3:
            #overwrite only the identicals info
            clusters_data[cluster.name]["identicals"] = _serialize_identicals(cluster.identicals)

        if new_cluster_name:
            stage = _change_name_in_clusters_yet_to_check(old_cluster_name, new_cluster_name, stage)
            stage = _change_name_in_clusters_done(old_cluster_name, new_cluster_name,stage)
            progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"] = {
                                                            "name":new_cluster_name,
                                                            "unprocessed_matches":[],
                                                            "unprocessed_nomatches":[],
                                                            "unprocessed_marked_coin_group_list": []
                                                            }
        else:
            progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"] = {
                                                                        "name":old_cluster_name,
                                                                        "unprocessed_matches":[],
                                                                        "unprocessed_nomatches":[],
                                                                        "unprocessed_marked_coin_group_list": []
                                                                        }
        progress_data[project_name]["stages"][str(stage.stage_number)]["clusters_yet_to_check"] = list(stage.clusters_yet_to_check)
        progress_data[project_name]["stages"][str(stage.stage_number)]["clusters_done"] = list(stage.clusters_done)
    
    #write new clusters_data
    progress_data[project_name]["clusters"] = clusters_data

    #delete previous stage info to reduce memory
    for i in range(stage.stage_number):
        if str(i) in progress_data[project_name]["stages"]:
            _ = progress_data[project_name]["stages"].pop(str(i))

    if write_to_json:
        write_progress_data_to_json(progress_data)
    return progress_data, stage

def clear_current_project(project_name, progress_data):
    """remove current project from progress data & delete project folder
    """
    if len(project_name) == 0:
        return
    if project_name in progress_data:
        _ = progress_data.pop(project_name)
    data_file = open("data.json", "w")
    json.dump(progress_data, data_file, indent = 4)
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
    data_file.close()
    #retrieve latest stage
    stage_number= max(progress_data[project_name]["stages"].keys())
    stage_info = progress_data[project_name]["stages"][stage_number]
    stage = Stage(int(stage_number), progress_data[project_name])
    stage.clusters_yet_to_check = set(stage_info["clusters_yet_to_check"])
    stage.clusters_done = set(stage_info["clusters_done"])
    #retrieve latest cluster
    current_cluster_name = stage_info["current_cluster"]["name"]
    if stage_number == "0":
        cluster_info = progress_data[project_name]["clusters"][current_cluster_name]
        cluster = Cluster( cluster_name = current_cluster_name,
            identicals = _deserialize_identicals(cluster_info["identicals"]),
            best_image_name = cluster_info["best_image_name"],
            images = cluster_info["images"],
            matches = set(cluster_info["matches"]).union(set(stage_info["current_cluster"]["unprocessed_matches"])),
            nomatches = set(cluster_info["nomatches"]).union(set(stage_info["current_cluster"]["unprocessed_nomatches"]))
        )
    else:
        # current cluster hasn't been completed yet. restore unprocessed info
        if current_cluster_name in stage.clusters_yet_to_check:
            cluster = _create_a_cluster(stage, progress_data[project_name]["clusters"],current_cluster_name)
            cluster.matches = cluster.matches.union(set(stage_info["current_cluster"]["unprocessed_matches"]))
            cluster.nomatches = cluster.nomatches.union(set(stage_info["current_cluster"]["unprocessed_nomatches"]))
            cluster.compared_before = (cluster.matches).union(cluster.nomatches)
        # if current cluster has already been checked. give the next cluster in line
        else:
            next_in_line = sorted(list(stage.clusters_yet_to_check), key= lambda s: s.split("_")[0])[0]
            cluster = _create_a_cluster(stage, progress_data[project_name]["clusters"], next_in_line)
            progress_data[project_name]["stages"][str(stage.stage_number)]["current_cluster"]["name"] = cluster.name

    unprocessed_marked_coin_group_list = [(item[0], item[1]) for item in stage_info["current_cluster"]["unprocessed_marked_coin_group_list"]]
    return progress_data, stage, cluster, unprocessed_marked_coin_group_list

def check_cluster_completion(cluster,stage):
    """Check if all images in the current cluster have all been processed
    """
    if not cluster:
        return True

    all_compared_already = all([(imgObj.name in cluster.compared_before or imgObj.name == cluster.best_image.name ) \
        for imgObj in cluster.images ])
    return all_compared_already


def check_stage_completion(stage, clusters_data):
    if stage.stage_number == 1:
        if (len(stage.clusters_yet_to_check) == 0) :
            return True
        elif (len(stage.clusters_yet_to_check) == 1 and len(clusters_data["Singles"]["images"]) == 0):
            logger.debug(f"[progress: check_stage_completion] Skip cluster {stage.clusters_yet_to_check}")
            return True
    elif stage.stage_number == 2:
        if (len(stage.clusters_yet_to_check) == 0):
            return True
        elif (len(clusters_data["Singles"]["images"]) <= 1):
            remaining_single = clusters_data["Singles"]["images"]
            logger.debug(f"progress: check_stage_completion] Skip single {remaining_single}")
            return True
        # elif  #TODO when everything has been compared before
    else:
        return len(stage.clusters_yet_to_check) == 0
    
    return False

def check_project_completion(stage, clusters_data):
    return check_stage_completion(stage, clusters_data) and stage.stage_number == 3


def check_part1_completion(cluster,stage, clusters_data):
    """
    part1 means all stages except the identicals vs identicals
    """
    stage_completed = check_stage_completion(stage, clusters_data)
    is_stage_two = stage.stage_number == 2
    case1 = stage_completed and is_stage_two

    #we are at the last cluster of stage 1 and we don't have any Single or cluster to compare with the last cluster
    case2 = stage.stage_number == 1 and check_cluster_completion(cluster, stage) \
        and len(stage.clusters_yet_to_check) == 1\
        and len(set(clusters_data["Singles"]["images"]).intersection(clusters_data[list(stage.clusters_yet_to_check)[0]]['nomatches'])) \
            == len(clusters_data["Singles"]["images"])  # all the remaining singles have already been compared with the last cluster and marked nomatches

    return case1 or case2

def mark_cluster_completed(cluster, stage, clusters_data):
    """Remove current cluster name from clusters_yet_to_check. Before updating cluster name"""

    if cluster.name in stage.clusters_yet_to_check:
        stage.clusters_yet_to_check.remove(cluster.name)
        stage.clusters_done.add(cluster.name)

    #Inspect Verified Stage and the rest: move the matched clusters off the yet_to_check list
    if stage.stage_number > 0 and stage.stage_number <3:
        best_image_cluster_dict = _create_best_image_cluster_dict(clusters_data)
        for image_name in cluster.matches:
            if stage.stage_number == 1 and image_name in best_image_cluster_dict:
                matched_cluster_name = best_image_cluster_dict[image_name]
            else:
                matched_cluster_name = image_name

            if matched_cluster_name in stage.clusters_yet_to_check:
                stage.clusters_yet_to_check.remove(matched_cluster_name)
                stage.clusters_done.add(matched_cluster_name)
    return stage

def unmark_cluster_completed(cluster,stage, clusters_data):
    """reverse marking cluster completed"""

    if cluster.name not in stage.clusters_yet_to_check:
        stage.clusters_yet_to_check.add(cluster.name)
        stage.clusters_done.remove(cluster.name)

    #Inspect Verified Stage and the rest: move the matched clusters off the yet_to_check list
    if stage.stage_number > 0 and stage.stage_number < 3:
        best_image_cluster_dict = _create_best_image_cluster_dict(clusters_data)
        for image_name in list(cluster.matches):
            if stage.stage_number == 1 and image_name in best_image_cluster_dict:
                matched_cluster_name = best_image_cluster_dict[image_name]
            else:
                matched_cluster_name = image_name
            if matched_cluster_name not in stage.clusters_yet_to_check:
                stage.clusters_yet_to_check.add(matched_cluster_name)
                stage.clusters_done.remove(matched_cluster_name)

    return stage

def copy_best_image_to_verified(cluster, project_name):
    project_folder = os.path.join(os.getcwd() ,"projects", project_name)
    if not os.path.exists(os.path.join(project_folder, "Verified")):
        os.mkdir(os.path.join(project_folder, "Verified"))
    old_image_address = os.path.join(cluster.address, cluster.best_image.name)
    new_image_address = os.path.join(project_folder, "Verified", cluster.name + ".jpg")
    shutil.copyfile(old_image_address, new_image_address)
    return cluster


def _create_a_cluster(stage, clusters_data, next_cluster_name, bump_up_queue = []):
    #compare within cluster
    if stage.stage_number == 0 :
        next_cluster = Cluster(cluster_name = next_cluster_name, 
        images = clusters_data[next_cluster_name]["images"], 
        identicals = [], 
        best_image_name = "", 
        matches = set(), 
        nomatches = set()) 

    #compare each cluster's best image with other cluster's best image and everything in "Singles", minus those that have been compared to the next cluster in stage 0
    elif stage.stage_number == 1:
        #filter the singles
        images_in_single = []
        for single in clusters_data["Singles"]["images"]:
            if single not in clusters_data[next_cluster_name]["nomatches"]:
                images_in_single.append(single)

        #filter the best images
        best_image_cluster_dict = {v["best_image_name"]: k for k, v in clusters_data.items() if not k == "Singles"}
        best_images = [i for i in best_image_cluster_dict if \
            ((i not in stage.clusters_done) and
            (best_image_cluster_dict[i] not in stage.clusters_done) and
            (i not in clusters_data[next_cluster_name]["nomatches"]) and
            (best_image_cluster_dict[i] != next_cluster_name)
             )]
        
        #modify the bump_up_queue to be a list of image names. The complexity of this step lies in the mix of Singles and normal clusters.
        #Images under Singles are named by their own name whereas those under a cluster is named after their cluster name
        bump_up_queue_image_name = []
        for item in bump_up_queue:
            if item in clusters_data:
                bump_up_queue_image_name.append(clusters_data[item]["best_image_name"])
            else:
                bump_up_queue_image_name.append(item)
    
        #create the cluster
        next_cluster = Cluster(cluster_name = next_cluster_name, 
        images =  images_in_single + best_images, 
        identicals = [], 
        best_image_name = clusters_data[next_cluster_name]["best_image_name"], 
        matches = set(), 
        nomatches = set(),
        bump_up_queue= bump_up_queue_image_name)

        #replace the image's cluster name with the cluster it represents for showing in the interface
        for image_name, image_object in next_cluster.images_dict.items():
            if image_name in best_image_cluster_dict:
                image_object.cluster = best_image_cluster_dict[image_name]
            else:
                image_object.cluster = "Singles"
            next_cluster.images_dict[image_name] = image_object

    elif stage.stage_number == 2:
        #A cluster should include all images in the Singles folder, except those have been matched
        images= [i for i in clusters_data["Singles"]["images"] if i not in stage.clusters_done]
        next_cluster = Cluster(cluster_name = next_cluster_name, 
        images = images, 
        identicals = [], 
        best_image_name = next_cluster_name, 
        matches = set(), 
        nomatches = set(),
        bump_up_queue = bump_up_queue)
        #replace the image's cluster name with the cluster it represents
        for image_name, image_object in next_cluster.images_dict.items():
            image_object.cluster = "Singles"
            next_cluster.images_dict[image_name] = image_object
    else:
        if next_cluster_name == "Singles":
            images = clusters_data[next_cluster_name]["images"]
        else:
            images = clusters_data[next_cluster_name]["matches"] + [clusters_data[next_cluster_name]["best_image_name"]]
        next_cluster = Cluster(cluster_name = next_cluster_name, 
        images = images,
        identicals = [], 
        best_image_name = "", 
        matches = set(images), #at stage 4, all images in the cluster folder have been marked as matches in the previous stages
        nomatches = set())
        
    return next_cluster

def create_next_cluster(stage, clusters_data, bump_up_next = None, bump_up_queue = []):
    """If the new cluster has only 1 image. the interface will take care of it"""
    if len(stage.clusters_yet_to_check) == 0:
        logger.debug(f"stage {stage.name} clusters yet to check is zero")
        return None
    
    if bump_up_next:
        next_cluster_name = bump_up_next[1]

    if (not bump_up_next) or (bump_up_next not in stage.clusters_yet_to_check):
        next_cluster_name = sorted(list(stage.clusters_yet_to_check),key= lambda s: s.split("_")[0])[0]
    else:
        next_cluster_name = bump_up_next
    if stage.stage_number == 1 or stage.stage_number == 2:
        next_cluster = _create_a_cluster(stage, clusters_data, next_cluster_name, bump_up_queue)
    else:
        next_cluster = _create_a_cluster(stage, clusters_data, next_cluster_name)
    return next_cluster


def create_next_stage( stage, project_data, bump_up_next, bump_up_queue):
    new_stage = Stage(stage.stage_number+1, project_data)
    logger.debug(f"Next stage {new_stage.name}. yet to check: {new_stage.clusters_yet_to_check}")
    new_cluster = create_next_cluster(new_stage, project_data["clusters"], bump_up_next, bump_up_queue)

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


def create_cluster_folders(project_name, clusters_data, dest_folder):
    project_folder = os.path.join(os.getcwd() ,"projects", project_name)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    dest_verified_folder = os.path.join(dest_folder, "Verified")
    if not os.path.exists(dest_verified_folder):
        os.makedirs(dest_verified_folder)

    for cluster_name, cluster_info in clusters_data.items():
        if cluster_name != "Singles":
            final_cluster_name = _concatenate_image_names_in_data(cluster_info)
            final_images = cluster_info["matches"]
        else:
            final_cluster_name = "Singles"
            final_images = cluster_info["images"]
        dest_cluster_folder = os.path.join(dest_folder, final_cluster_name)
        if not os.path.exists(dest_cluster_folder):
            os.makedirs(dest_cluster_folder)

        for image_name in final_images:
            shutil.copy(os.path.join(project_folder, image_name), os.path.join(dest_cluster_folder, image_name))

        if cluster_name != "Singles":
            if len(cluster_info["best_image_name"]) > 0 and cluster_info["best_image_name"] not in cluster_info["matches"]:
                shutil.copy(os.path.join(project_folder, cluster_info["best_image_name"]), os.path.join(dest_cluster_folder, cluster_info["best_image_name"]))
                #copy best image to verified
            shutil.copy(os.path.join(project_folder, cluster_info["best_image_name"]),os.path.join(dest_verified_folder, final_cluster_name + '.' + cluster_info["best_image_name"].split(".")[-1]))

def export_results(project_name, progress_data, save_address, project_code):
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
    all_singles =  progress_data[project_name]["clusters"]["Singles"]["images"]
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
    digits = max(3, len(str(int(res.index.values[-2]))))
    res.index = [project_code + ';' + str(int(idx) + 1).zfill(digits) for idx in res.index]
    res = res.rename(index={res.index[-1]: ""})

    project_folder = os.path.join(os.getcwd() ,"projects", project_name)
    project_folder_name = os.path.basename(project_folder) + "_" + str(datetime.now().strftime('%Y-%m-%d-%H-%M'))
    dest_folder = os.path.join(save_address, project_folder_name)
    create_cluster_folders(project_name, progress_data[project_name]["clusters"], dest_folder)

    res.to_excel( os.path.join(dest_folder, "results_" + project_folder_name + ".xlsx"), index= True)

    return dest_folder

def _create_best_image_cluster_dict (clusters_data):
    return {v["best_image_name"]: k for k, v in clusters_data.items() if not k == "Singles"}

def create_new_objects(cluster, stage, project_name, progress_data, completion_status, bump_up_next = None, bump_up_queue = []):
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
            new_cluster, new_stage = create_next_stage(stage, progress_data[project_name], bump_up_next, bump_up_queue)
            while ((not new_cluster) or check_stage_completion(new_stage, progress_data[project_name]["clusters"])):
                logger.debug(f"[progress.py: create_new_objects] Skip stage {new_stage.name}")
                new_cluster, new_stage = create_next_stage(new_stage,progress_data[project_name], bump_up_next, bump_up_queue)
            return new_cluster, new_stage
    else:
        clusters_data = progress_data[project_name]["clusters"]
        new_cluster = create_next_cluster(stage, clusters_data, bump_up_next, bump_up_queue)

        #If the new cluster is already completed: skip TODO:this part should be outside of this function
        if stage.stage_number < 3:
            while check_cluster_completion(new_cluster, stage):
                logger.debug(f"[progress.py: create_new_objects] Skip cluster {new_cluster.name}")
                stage = mark_cluster_completed(new_cluster, stage,progress_data[project_name]["clusters"])
                if check_stage_completion(stage,progress_data[project_name]["clusters"]):
                    if check_project_completion(stage, progress_data[project_name]["clusters"]):
                        return None, stage
                    else:
                        return create_new_objects(new_cluster, stage, project_name, progress_data, "stage", bump_up_next, bump_up_queue)
                else:
                    return create_new_objects(new_cluster, stage, project_name, progress_data, "cluster", bump_up_next, bump_up_queue)
        return new_cluster, stage

def create_image_folder(old_project_address, new_project_address):
    """Create a folder under /project by copying images from project_folder
    """
    if not os.path.exists(new_project_address):
        os.makedirs(new_project_address)
    for file_extension in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
        for file_path in glob.glob(os.path.join(old_project_address, '**', file_extension), recursive=True):
            new_path = os.path.join(new_project_address, os.path.basename(file_path))
            shutil.copy(file_path, new_path)

def import_progress_data(image_folder_address, imported_project_name, imported_project_data):
    """Import function for restoring progress data from another project

    Args:
        image_folder (_type_): _description_
        project_data (dict): 
    """
    if len(imported_project_name) == 0 or len(imported_project_data) == 0:
        return

    data_file = open(os.path.join(os.getcwd(), "data.json"), "r")
    existing_progress_data = json.loads(data_file.read())
    existing_project_names = existing_progress_data.keys()
    project_name = imported_project_name
    while project_name in existing_project_names:
        project_name += "_"
    existing_progress_data[project_name] = imported_project_data[imported_project_name]
    data_file = open(os.path.join(os.getcwd(), "data.json"), "w")
    json.dump(existing_progress_data, data_file, indent= 4)
    data_file.close()
    
    new_project_address = os.path.join(os.getcwd(),"projects",project_name)
    create_image_folder(image_folder_address, new_project_address)
    logger.info(f"Import project {project_name}")

def get_existing_project_names():
    data_file = open(os.path.join(os.getcwd(), "data.json"), "r")
    existing_progress_data = json.loads(data_file.read())
    existing_project_names = existing_progress_data.keys()
    data_file.close()
    return set(existing_project_names)
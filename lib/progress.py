"""
This module has three main functionalities:
1. Save intermediate result to a json file.
2. Read previous results into objects
3. Update the file structures according to matches

When are data saved? :
1. When user clicks "Save" button
2. When user moves to the next cluster/ stage

What data are saved & read? :
1. Current stage number & images checked
2. The current cluster address, list of identicals, set of matches, set of nomatches, best image address

When are data removed? :
1. When project is completed & excel file is exported
"""
import json
from objects import *
import os
import shutil
import pandas as pd
from root_logger import * 

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

def _collect_identicals(cluster):
    identical_group_list = []
    identical_name_list =[]
    for identical_set in sorted(cluster.identicals):
        identical_group_name = ""
        prev_type = ""

        for image_name in sorted(identical_set):
            image_id = image_name.split(".")[0] #without .jpg
            identical_name_list.append(image_id)
            curr_type, curr_name = image_id.split(";")
            if curr_type != prev_type:
                identical_group_name += image_id
            else:
                identical_group_name += str("_" + curr_name)
            prev_type = curr_type
        identical_group_list .append(identical_group_name)

    #best image, not part of the matches, may be part of the identicals
    if cluster.best_image.id not in identical_name_list:
        identical_group_list.append(cluster.best_image.id)

    return identical_group_list, identical_name_list

def _concatenate_image_names(cluster):
    """get cluster name"""
    identical_group_list, identical_name_list = _collect_identicals(cluster)

    matches = []

    for image_name in sorted(cluster.matches):
        image_id = image_name.split(".")[0]
        if image_id not in identical_name_list:
            matches.append(image_id)

    final_names = identical_group_list + matches

    return "_".join(sorted(final_names))

def start_new_project(original_project_folder, project_name):
    new_project_folder =os.getcwd() +"/projects" + "/" + project_name
    shutil.copytree(original_project_folder, new_project_folder)
    data_file = open("data.json", "r")
    progress_data = json.loads(data_file.read())

    if not os.path.exists(new_project_folder + "/Verified"):
        os.mkdir(new_project_folder + "/Verified")

    return new_project_folder, progress_data

def cluster_validation_update_folder_and_record(progress_data, project_folder, cluster):
    """
    1. update images in cluster folder (move nomatches to Singles)
    2. update cluster names in folder and in record (progress_data)
    3. Put best image in verified folder
    4. (done in save_progress) If the cluster has only 1 image left. Move that image to Singles & delete cluster folder & record"""


    for image_object in cluster.images:
        is_nomatch = image_object.name in cluster.nomatches
        old_image_address = image_object.address

        if is_nomatch:
            new_image_address = project_folder + "/Singles/"+ image_object.name
            image_object.address = new_image_address
            shutil.move(old_image_address, new_image_address)

    if len(cluster.matches) == 0 and len(cluster.nomatches) > 0:
        return progress_data, cluster

    #only rename cluster when it's completed
    if check_cluster_completion(cluster):
        new_cluster_name = _concatenate_image_names(cluster)
    else:
        new_cluster_name = cluster.name
    new_cluster_address = project_folder + "/" + new_cluster_name

    shutil.move(cluster.address, new_cluster_address)

    #update cluster name in record
    if project_folder in progress_data and cluster.name in progress_data[project_folder]["clusters"]:
        progress_data[project_folder]["clusters"][new_cluster_name] = progress_data[project_folder]["clusters"].pop(cluster.name)


    #update cluster object
    cluster.name = new_cluster_name
    cluster.address = new_cluster_address

    #copy best image to verified only if cluster is completed
    if check_cluster_completion(cluster):
        copy_best_image_to_verified(cluster, project_folder)

    return progress_data, cluster

def inspect_verified_update_folder_and_record(progress_data, project_folder, cluster):
    """
    1. Move all images in the matched clusters into the current cluster.
    2. Delete the matched clusters
    3. Rename the current cluster #??? what if there are identicals across two clusters
    4. Rename the current cluster in record. Add images to matches
    5. Rename the best image of the current cluster in Verified folder with the new name
    6. If the cluster has no matches and all nomatches ->
    """
    #1
    list_of_matches = list(cluster.matches)
    left_cluster_address = project_folder + "/" + cluster.name
    for matched_cluster_name_jpg in list_of_matches:
        matched_cluster_name = matched_cluster_name_jpg.split(".")[0]
        matched_cluster_address = project_folder+ "/"+ matched_cluster_name
        image_names = os.listdir(matched_cluster_address)

        for image_name in image_names:
            if not image_name.startswith('.'):
                cluster.matches.add(image_name)
                shutil.move(str(matched_cluster_address+"/"+image_name), str(left_cluster_address+ "/" + image_name))

        matched_cluster_identicals = progress_data[project_folder]["clusters"][matched_cluster_name]["identicals"]
        left_cluster_identicals = progress_data[project_folder]["clusters"][cluster.name]["identicals"]
        progress_data[project_folder]["clusters"][cluster.name]["identicals"]= left_cluster_identicals + matched_cluster_identicals

        #2
        shutil.rmtree(matched_cluster_address)
        logger.info("Remove {}".format(matched_cluster_address))
        os.remove(str(project_folder + "/Verified/" + matched_cluster_name_jpg))
        progress_data[project_folder]["clusters"].pop(matched_cluster_name)

    #3
    old_cluster_name = cluster.name
    old_cluster_address = left_cluster_address
    new_cluster_name = old_cluster_name
    for matched_cluster_name_jpg in cluster.matches:
        new_cluster_name += "_" + matched_cluster_name_jpg.split(".")[0]

    logger.info("Verified new cluster name: {}".format(new_cluster_name))
    new_cluster_address = project_folder+ "/" + new_cluster_name
    shutil.move(old_cluster_address, new_cluster_address)
    cluster.name = new_cluster_name
    cluster.address = new_cluster_address

    #4
    progress_data[project_folder]["clusters"][new_cluster_name] = progress_data[project_folder]["clusters"].pop(old_cluster_name)

    #5
    shutil.move(project_folder+"/Verified/"+old_cluster_name +".jpg", project_folder+"/Verified/"+new_cluster_name +".jpg")

    data_file = open("data.json", "w")
    json.dump(progress_data, data_file)
    data_file.close()
    return progress_data, cluster

def verified_vs_singles_update_folder_and_record (progress_data, project_folder, cluster):
    """
    Left: verified Right: single
    Each cluster will have 1 verified as the "best image" and in its matches those singles that belong to the cluster
    1. Move all matches into the verified cluster
    2. Delete the matched singles from "Singles" folder
    3. Rename the verified cluster #??? what if there are identicals across two clusters
    4. Rename the verified cluster in record. Add matched singles to its matches
    5. Rename the best image of the current cluster in Verified folder with the new name
    6. If the cluster has only 1 image, return progress data and None
    """
    # if len(cluster.images)  <= 1:
    #     if project_folder in progress_data and cluster.name in progress_data[project_folder]["clusters"]:
    #         progress_data[project_folder]["clusters"].pop(cluster.name)
    #     cluster = None
    #     return progress_data, cluster

    #1
    list_of_matches = list(cluster.matches)
    left_cluster_address = project_folder + "/" + cluster.name
    for matched_single_name_jpg in list_of_matches:
        matched_single_name = matched_single_name_jpg.split(".")[0]
        single_address = project_folder+ "/Singles"
        shutil.move(str(single_address+"/"+matched_single_name_jpg), str(left_cluster_address+ "/" + matched_single_name_jpg))

    #3
    old_cluster_name = cluster.name
    old_cluster_address = left_cluster_address
    new_cluster_name = _concatenate_image_names(cluster)
    new_cluster_address = project_folder+ "/" + new_cluster_name
    shutil.move(old_cluster_address, new_cluster_address)
    cluster.name = new_cluster_name
    cluster.address = new_cluster_address

    #4
    progress_data[project_folder]["clusters"][new_cluster_name] = progress_data[project_folder]["clusters"].pop(old_cluster_name)

    #5
    shutil.move(project_folder+"/Verified/"+old_cluster_name +".jpg", project_folder+"/Verified/"+new_cluster_name +".jpg")

    data_file = open("data.json", "w")
    json.dump(progress_data, data_file)
    data_file.close()
    return progress_data, cluster

def single_vs_single_update_folder_and_record(progress_data, project_folder, cluster):
    """
    Left: the single that represent its own cluster 
    Right: another single
    1. Move all matches and best image into a new cluster folder with new name
    2. Add the new cluster to record (? or leave it to save_progress)
    3. Add the best image of the new cluster to verified & rename
    4. Update the cluster object
    """
    if len(cluster.matches) == 0 or len(cluster.images) <= 1 :
        return None

    else:
        new_cluster_address = project_folder + "/temp_new_cluster"
        os.mkdir(new_cluster_address)
        for image_name in cluster.matches:
            image_obj = cluster.images_dict[image_name]
            new_image_address = new_cluster_address + "/" + image_obj.name
            shutil.move(image_obj.address, new_image_address)

        shutil.move(cluster.best_image.address, new_cluster_address + "/" + cluster.best_image.name)

        new_cluster = Cluster(new_cluster_address, None, cluster.identicals, cluster.best_image.name, cluster.matches, set())
        new_cluster_name = _concatenate_image_names(new_cluster)
        new_cluster.name = new_cluster_name
        new_cluster_address = project_folder + "/" + new_cluster_name
        new_cluster.address = new_cluster_address
        shutil.move(project_folder + "/temp_new_cluster", new_cluster_address)

        #3
        copy_best_image_to_verified(new_cluster, project_folder)

        return progress_data, new_cluster

def update_folder_and_record(progress_data, project_folder, cluster, stage):
    """
    This update will happen automatically when user completes a cluster or click "save"
    all changes will be made to the new project folder.

    """
    if stage.stage_number == 0:
        return cluster_validation_update_folder_and_record(progress_data, project_folder, cluster)
    elif stage.stage_number == 1:
        return inspect_verified_update_folder_and_record(progress_data, project_folder, cluster)
    elif stage.stage_number == 2:
        return verified_vs_singles_update_folder_and_record(progress_data, project_folder, cluster)
    elif stage.stage_number == 3:
        return single_vs_single_update_folder_and_record(progress_data, project_folder, cluster)
    #TODO next: add more stages



def save_progress_data(project_folder, stage, cluster, progress_data):
    """
    save all work done in this session
    format
    {"project_folder1" : {  "clusters": {cluster_name: {
                                                        "cluster_address":,
                                                        "cluster_name:,
                                                        "identicals":,
                                                        "matches":,
                                                        "nomatches":
                                                    }
                                            }
                            "stages": { 0: {
                                        "current_cluster" : ,
                                        "clusters_yet_to_check": []}}
    }

    *the update on "clusters" will only happen for stage 0
    """
    #new project
    if project_folder not in progress_data:
        progress_data[project_folder] = {"clusters": {}, "stages": {}}

    #new stage
    if str(stage.stage_number) not in progress_data[project_folder]["stages"]:
        progress_data[project_folder]["stages"][str(stage.stage_number)] ={
        "clusters_yet_to_check": list(stage.clusters_yet_to_check)
        }

    #if Cluster is None (end of project) then do nothing
    if cluster:
        #if the cluster has only 1 image -> move that to singles
        cluster_images = [f for f in os.listdir(cluster.address) if not f.startswith('.')]
        if stage.stage_number == 0 and len(cluster_images) == 1:
            shutil.move(cluster.best_image.address, project_folder + "/Singles/" + cluster.best_image.name)
            shutil.rmtree(cluster.address)

            if project_folder in progress_data and cluster.name in progress_data[project_folder]["clusters"]:
                progress_data[project_folder]["clusters"].pop(cluster.name)

        else:
            #update current cluster
            progress_data[project_folder]["stages"][str(stage.stage_number)]["current_cluster"] = cluster.name

            if stage.stage_number == 0:
                #overwrite cluster info
                progress_data[project_folder]["clusters"][cluster.name] = {
                    "cluster_address": cluster.address,
                    "cluster_name": cluster.name,
                    "identicals": _serialize_identicals(cluster.identicals),
                    "matches": list(cluster.matches),
                    "nomatches": list(cluster.nomatches),
                    "best_image_name": cluster.best_image.name
                    }
            elif stage.stage_number == 3:
                if cluster.name not in progress_data[project_folder]["clusters"] and len(cluster.matches) > 0:
                    progress_data[project_folder]["clusters"][cluster.name] = {
                    "cluster_address": cluster.address,
                    "cluster_name": cluster.name,
                    "identicals": _serialize_identicals(cluster.identicals),
                    "matches": list(cluster.matches),
                    "nomatches": list(cluster.nomatches),
                    "best_image_name": cluster.best_image.name
                    }

            #update current cluster
            progress_data[project_folder]["stages"][str(stage.stage_number)]["current_cluster"] = cluster.name
            #update clusters_yet_to_check
            progress_data[project_folder]["stages"][str(stage.stage_number)]["clusters_yet_to_check"] = list(stage.clusters_yet_to_check)
    data_file = open("data.json", "w")
    json.dump(progress_data, data_file)
    data_file.close()

def checkout_progress():
    """read progress data
    """
    data_file = open("data.json", "r")
    progress_data = json.loads(data_file.read())
    return progress_data

def load_progress(project_folder, create_next_cluster = True):
    """read progress data and create objects"""
    data_file = open("data.json", "r")
    progress_data = json.loads(data_file.read())
    #retrieve latest stage
    stage_number= max(progress_data[project_folder]["stages"].keys())
    stage_info = progress_data[project_folder]["stages"][stage_number]
    stage = Stage(int(stage_number), project_folder)
    stage.clusters_yet_to_check = set(stage_info["clusters_yet_to_check"])
    #retrieve latest cluster
    current_cluster = stage_info["current_cluster"]
    if not create_next_cluster:
        return progress_data, stage, None
    if stage_number == "0":
        cluster_info = progress_data[project_folder]["clusters"][current_cluster]
        cluster = Cluster(cluster_info["cluster_address"], current_cluster,
        _deserialize_identicals(cluster_info["identicals"]),
        cluster_info["best_image_name"],
        set(cluster_info["matches"]),
        set(cluster_info["nomatches"]))
    else:
        if len(stage.clusters_yet_to_check) == 0:
            cluster = None
        elif current_cluster in stage.clusters_yet_to_check:
            cluster = _create_a_cluster(stage,project_folder,current_cluster)
        # if current cluster has already been checked. give the next cluster in line
        else:
            next_in_line = list(stage.clusters_yet_to_check)[0]
            cluster = _create_a_cluster(stage, project_folder, next_in_line)
            progress_data[project_folder]["stages"][str(stage.stage_number)]["current_cluster"] = cluster.name

    if len(stage.clusters_yet_to_check) == 0:
        #TODO add view cluster mode
        pass

    return progress_data, stage, cluster

# before saving progress, check for stage and completion.
# if completed, then save current stage/cluster, then update current stage/cluster to the next in line.
# save the new cluster/stage to progress so that next time the user opens the project, they will see the new cluster

def check_cluster_completion(cluster):
    """Check if all images in the current cluster have all been processed
    Cluster == None is for situations where the completed cluster has only 1 image & get deleted
    """
    return cluster == None or (len(cluster.matches) + len(cluster.nomatches) == len(cluster.images) - 1)

def check_stage_completion(cluster, stage):
    stage_complete = len(stage.clusters_yet_to_check) == 0
    last_cluster_complete = check_cluster_completion(cluster) and len(stage.clusters_yet_to_check) == 1 and cluster.name == list(stage.clusters_yet_to_check)[0]
    return stage_complete or last_cluster_complete

def check_project_completion(cluster, stage, project_folder):
    stage_completed = check_stage_completion(cluster, stage)
    is_last_stage = stage.stage_number == 3
    case1 = stage_completed and is_last_stage

    #case2 we are at stage 1 and there is no singles in the folder
    singles_in_folder = [f for f in str(project_folder + "/Singles") if not f.startswith('.')]
    case2 = stage.stage_number == 1 and len(singles_in_folder) == 0

    #case3 we are at stage 2 or 3 and took all images (or all but one image) in "Singles" to the current cluster
    case3 = (stage.stage_number >= 2) and check_cluster_completion(cluster) and len(cluster.nomatches) <= 1

    return case1 or case2 or case3

def mark_cluster_completed(cluster, stage):
    """Remove current cluster name from clusters_yet_to_check. Before updating cluster name"""
    cluster_id = cluster.name.split(".")[0]
    if cluster_id in stage.clusters_yet_to_check:
        stage.clusters_yet_to_check.remove(cluster_id)

    #Inspect Verified Stage: move the matched clusters off the yet_to_check list
    if stage.stage_number > 0:
        for image_name in list(cluster.matches):
            if image_name.split(".")[0] in stage.clusters_yet_to_check:
                stage.clusters_yet_to_check.remove(image_name.split(".")[0])

    return stage

def copy_best_image_to_verified(cluster, project_folder):
    if not os.path.exists(project_folder + "/Verified"):
        os.mkdir(project_folder + "/Verified")
    old_image_address = cluster.address + "/" + cluster.best_image.name
    new_image_address = project_folder + "/Verified/" + cluster.name + ".jpg"
    shutil.copyfile(old_image_address, new_image_address)
    logger.info("Copied best image of {} to Verified".format(cluster.name))
    return cluster

def _create_a_cluster(stage,project_folder, next_cluster_name):
    if stage.stage_number == 0:
        next_cluster = Cluster(str(project_folder +"/"+next_cluster_name), cluster_name = None, identicals = [], best_image_name = None, matches = set(), nomatches = set())

    elif stage.stage_number == 1:
        #treat the entire Verified folder as a cluster,
        # minus those images that were previously matched (done in mark_cluster_complete)

        best_image_name = next_cluster_name+".jpg"
        next_cluster = Cluster(str(project_folder +"/Verified"), cluster_name = next_cluster_name, identicals = [], best_image_name = best_image_name, matches = set(), nomatches = set())

        #replace the image's cluster name with the cluster it represents
        new_images_dict = {}

        for image_name in next_cluster.images_dict:
            new_image_obj = next_cluster.images_dict[image_name]
            new_image_obj.cluster = image_name.split(".")[0]
            new_images_dict[image_name] = new_image_obj

        next_cluster.images_dict = new_images_dict

    elif stage.stage_number == 2:
        #A cluster should include all images in the Singles folder + best_image from one of the Verified. Cluster named after verified
        # TODO disable "Best_image"
        best_image_name = next_cluster_name
        best_image_name_jpg = best_image_name +".jpg"
        best_image_address = project_folder + "/Verified/" + best_image_name_jpg
        next_cluster = Cluster(str(project_folder +"/Singles"), cluster_name = next_cluster_name, identicals = [], matches = set(), nomatches = set())
        #replace the image's cluster name with the cluster it represents
        new_images_dict = {}
        for image_name in next_cluster.images_dict:
            new_image_obj = next_cluster.images_dict[image_name]
            new_image_obj.cluster = "Singles"
            new_images_dict[image_name] = new_image_obj

        next_cluster.images_dict = new_images_dict

        #set the best image
        best_image_obj = ImgObj(best_image_address, best_image_name)
        next_cluster.images_dict[best_image_name] = best_image_obj
        next_cluster.images = [best_image_obj] + next_cluster.images
        next_cluster.best_image = best_image_obj

    elif stage.stage_number == 3:
        #A cluster should include all images in the Singles folder, except those have been matched

        best_image_name = next_cluster_name
        best_image_name_jpg = best_image_name +".jpg"
        best_image_address = project_folder + "/Singles/" + best_image_name_jpg

        next_cluster = Cluster(str(project_folder +"/Singles"), cluster_name = next_cluster_name, identicals = [], best_image_name = best_image_name_jpg, matches = set(), nomatches = set())
        #replace the image's cluster name with Singles
        new_images_dict = {}
        for image_name in next_cluster.images_dict:
            new_image_obj = next_cluster.images_dict[image_name]
            new_image_obj.cluster = "Singles"
            new_images_dict[image_name] = new_image_obj

        next_cluster.images_dict = new_images_dict

    logger.info("New cluster {}. Stage number {}".format(next_cluster_name, str(stage.stage_number)))
    return next_cluster

def create_next_cluster(cluster, stage, project_folder):
    """If the new cluster has only 1 image. the interface will take care of it"""
    if len(stage.clusters_yet_to_check) == 0:
        return None

    next_cluster_name = list(stage.clusters_yet_to_check)[0]
    logger.info("Create next cluster {}".format(next_cluster_name))
    return _create_a_cluster(stage, project_folder, next_cluster_name)


def create_next_stage(cluster, stage, project_folder):
    new_stage = Stage(stage.stage_number+1, project_folder)
    logger.info("Next stage. yet to check: {}".format(str(new_stage.clusters_yet_to_check)))
    new_cluster = create_next_cluster(cluster, new_stage, project_folder)

    return new_cluster, new_stage

def _concatenate_identicals(identicals):
    final_name = ""
    number_to_deduct = 0
    for identical_set in sorted(identicals):
        identical_group_name = ""
        prev_type = ""

        for image_name in sorted(identical_set):
            image_id = image_name.split(".")[0] #without .jpg
            curr_type, curr_name = image_id.split(";")
            if curr_type != prev_type:
                identical_group_name += image_id
            else:
                identical_group_name += str("_" + curr_name)
            prev_type = curr_type
        final_name += str("(" + identical_group_name +")")
        number_to_deduct += len(identical_set) - 1
    return final_name, number_to_deduct

def export_results(project_folder, progress_data, save_address):
    """Generate excel sheet & move cluster out & wipe out progress data"""
    clusters = progress_data[project_folder]["clusters"]
    max_length = 0
    total_number = 0
    for _, cluster in clusters.items():
        max_length = max(max_length, 1 + len(cluster["matches"]))

    columns = list(range(max_length)) + ["Identical", "Num"]
    data = []
    for _, cluster in clusters.items():
        all_images = cluster["matches"] + [cluster["best_image_name"]]
        all_images = sorted(list(all_images))
        data_row = all_images + [""] * (max_length - len(all_images))
        identicals = cluster["identicals"]
        final_name, number_to_deduct = _concatenate_identicals(identicals)
        data_row.append(final_name)
        data_row.append(str(len(all_images) - number_to_deduct))
        total_number += len(all_images) - number_to_deduct
        data.append(data_row)

    all_singles = [f for f in os.listdir(str(project_folder + "/Singles")) if not f.startswith('.')]
    for single_jpg in all_singles:
        data_row = [single_jpg.split(".")[0]] + [""] * (max_length - 1)
        data_row.append("")
        data_row.append(str(1))
        data.append(data_row)
        total_number += 1

    data.append([""] * max_length +["sum"] + [str(total_number)])
    res = pd.DataFrame(data, columns=columns)
    res = res.applymap(lambda x : x.split('.')[0])

    project_folder_name = project_folder.split("/")[-1]

    #move folders
    shutil.move(project_folder, save_address + "/" + project_folder_name)
    res.to_csv(save_address + "/" + project_folder_name + "/" + "results_" + project_folder_name + ".csv", index= False)

    #wipe out the records in progress data
    _  = progress_data.pop(project_folder)

    data_file = open("data.json", "w")
    json.dump(progress_data, data_file)
    data_file.close()
    return res


def check_completion_and_save(cluster, stage, project_folder, progress_data):
    """
    This function is called when user clicks "save" or "exit"
    Called after "update_folder_and_record" is done
    """

    save_progress_data(project_folder,stage,cluster,progress_data)

    new_progress_data = checkout_progress()

    if check_project_completion(cluster,stage, project_folder):
        pass
    else:
        if check_stage_completion(cluster, stage):
            new_cluster, new_stage = create_next_stage(cluster, stage, project_folder)
            save_progress_data(project_folder,new_stage, new_cluster, new_progress_data)

        else:
            if check_cluster_completion(cluster):
                new_cluster = create_next_cluster(cluster, stage, project_folder)
                save_progress_data(project_folder,stage, new_cluster, new_progress_data)

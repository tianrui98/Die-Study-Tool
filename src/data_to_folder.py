from src.progress import *

clusters_data =  {}

def export_data_to_folder():
    project_folder = "/Users/rui/Desktop/Die-Study-Tool/projects/Pre_ref_gold_Dec9"
    progress_data = {project_folder: clusters_data}
    save_address = "/Users/rui/Desktop"
    keep_progress = True
    export_results(project_folder, progress_data, save_address, keep_progress)
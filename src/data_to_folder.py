from src.progress import *

progress_data = {}

#the path name in the progress data from activities.log
project_name = "eastern (8-july-22) prediction"
#original folder with AI-computed clusters
project_folder = "/Users/rui/DieHards Dropbox/Glenn Data/eastern (8-july-22) prediction"
#where do you wish to save the exported folders
save_address = "/Users/rui/Desktop"

def create_image_folder(new_project_address):
    """Create a folder under /projecct by copying images from project_folder
    """
    if not os.path.exists(new_project_address):
        os.makedirs(new_project_address)
    for file_extension in ("*.jpg", "*.jpeg", "*.png"):
        for file_path in glob.glob(os.path.join(project_folder, '**', file_extension), recursive=True):
            new_path = os.path.join(new_project_address, os.path.basename(file_path))
            shutil.copy(file_path, new_path)

def export_data_to_folder():
    new_project_address =os.path.join(save_address, f"{project_name}_recovered")
    create_image_folder(new_project_address)

    new_progress_data = {new_project_address: progress_data[project_name]}
    keep_progress = True
    export_results(new_project_address, new_progress_data, save_address, keep_progress)

def restore_progress():
    """read progress data and create objects"""
    app_folder = str(Path(__file__).resolve().parent.parent)

    new_project_address = os.path.join(app_folder,"projects",f"{project_name}_recovered")
    create_image_folder(new_project_address)

    data_file = open(os.path.join(app_folder, "data.json"), "r")
    existing_progress_data = json.loads(data_file.read())
    existing_progress_data[f"{project_name}_recovered"] = progress_data[project_name]
    data_file = open(os.path.join(app_folder, "data.json"), "w")
    json.dump(existing_progress_data, data_file)
    data_file.close()
    print(f"Project {project_name} data restored")

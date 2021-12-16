from json import load
from src.main_interface import MainUI
from src.identical_interface import IdenticalUI
from src.progress import load_progress
import os

def main():
    MainUI().start()

def identical():
    IdenticalUI().start()

def test_identical():
    test_folder_address = os.path.join("test", "test_identical_long")
    test_cluster_address = os.path.join(test_folder_address, "test_cluster")
    test_data_address = os.path.join(test_folder_address, "test_data.json")

    progress_data, stage, cluster = load_progress(test_cluster_address, True, test_data_address)
    UI = IdenticalUI(project_name="test", project_address=test_cluster_address, progress_data= progress_data, cluster = cluster, stage = stage)
    UI.start()

if __name__ == "__main__":
    main()
    # test_identical()

#todo:
#1. allow the option to clear cache when user clicks exit. do not save by default
#2. remove identical button in the main UI
#3. add project title and cluster name to the identical UI
#4. merge two UIs
#5. auto clear old log.. only keep the latest one
#6. implement menu buttons for identical UI
#7. continue existing project mode -> enable open identical UI if stage == 4
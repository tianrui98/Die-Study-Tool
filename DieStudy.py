from src.main_interface import MainUI
from src.identical_interface import IdenticalUI
from src.progress import load_progress
import os
from src.data_to_folder import *

def main():
    MainUI().start()

def test_identical():
    """
    Manual testing
    """
    test_folder_address = os.path.join("test", "test_identical_long")
    test_cluster_address = os.path.join(test_folder_address, "test_cluster")
    test_data_address = os.path.join(test_folder_address, "test_data.json")
    progress_data, stage, cluster = load_progress(test_cluster_address, True, test_data_address)
    UI = IdenticalUI(project_name="test", project_address=test_cluster_address, progress_data= progress_data, cluster = cluster, stage = stage)
    UI.start()

def test_main():
    """
    Semi-automated testing. User still has to click the buttons but the actions will be recorded and compared with progress_data
    Must start fresh.
    """
    MainUI(testing_mode = True).start()

if __name__ == "__main__":
    print(f"Version updated on 28 May 2022. Main branch.")
    main()


#todo
#1. add save midway - done
#2. make it easier to share restored data (path issue)
#3. exit button currently stores the previous cluster. - done
#4. when user reaches the end of cluster but skipped some images. direct them to those skipped images
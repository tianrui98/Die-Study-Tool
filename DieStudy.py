from json import load
from src.main_interface import MainUI
from src.identical_interface import IdenticalUI
from src.progress import load_progress
import os
from src.data_to_folder import *
import tracemalloc
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
    tracemalloc.start()
    main()
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print("[ Top 10 ]")
    for stat in top_stats[:10]:
        print(stat)
    # test_identical()

#TODO
# fix continue existing project cannot open bug
#1. Reduce memory usage (currently increases at Step 1)
#2. Display clusters in ascending order
#3. Implement test mode
#4. Remove matches / no matches from progress data. It should only be used in objects
#5. replace all progress_data with project_data
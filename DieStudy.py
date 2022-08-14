from src.UI import UI
from src.progress import load_progress
import os
from src.data_to_folder import *

def main():
    UI().start()

def test_main():
    """
    Semi-automated testing. User still has to click the buttons but the actions will be recorded and compared with progress_data
    Must start fresh.
    """
    UI(testing_mode = True).start()

if __name__ == "__main__":
    main()


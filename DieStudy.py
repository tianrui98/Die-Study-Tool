from typing import Optional
from src.UI import UI
import argparse
from reset import *

__version__ = 20231217
parser = argparse.ArgumentParser()
parser.add_argument('-t', "--test" , action= "store_true", help='test mode.')
parser.add_argument('-r', "--reset", action= "store_true", help='clear all data.')
args = parser.parse_args()

def main():
    UI().start()

def test_main():
    """
    Semi-automated testing. User still has to click the buttons but the actions will be recorded and compared with progress_data
    Must start fresh.
    """
    UI(testing_mode = True).start()
    print(f"Latest update: {__version__}")


if __name__ == "__main__":
    if args.reset:
        print("Reset.")
        reset()
    if args.test:
        print("Test mode.")
        test_main()
    else:
        main()
    
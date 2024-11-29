from src.UI import UI
import argparse
from reset import *
from src.root_logger import *

__version__ = 20241128
logger.info(f"Latest update: {__version__}")

parser = argparse.ArgumentParser()
parser.add_argument('-t', "--test" , action= "store_true", help='test mode.semi-automated test.')
parser.add_argument('-r', "--reset", action= "store_true", help='clear all data after exit.')
args = parser.parse_args()

def main():
    UI().start()

def test_main():
    """
    Semi-automated testing. User still has to click the buttons but the actions will be recorded and compared with progress_data
    Must start fresh.
    """
    UI(testing_mode = True).start()

if __name__ == "__main__":
    if args.reset:
        print("Reset.")
        reset()
    if args.test:
        print("Test mode.")
        test_main()
    else:
        main()

from typing import Optional
from src.UI import UI
import argparse
from reset import *

parser = argparse.ArgumentParser()
parser.add_argument('test', metavar = "test", nargs='?', help='test mode.')
parser.add_argument('reset', metavar = "reset", nargs='?', help='clear all data.')
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
    if args.reset == "reset":
        print("Reset.")
        reset()
    if args.test == "test":
        print("Test mode.")
        test_main()
    else:
        main()
    
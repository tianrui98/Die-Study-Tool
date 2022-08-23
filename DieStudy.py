from src.UI import UI

def main():
    UI().start()

def test_main():
    """
    Semi-automated testing. User still has to click the buttons but the actions will be recorded and compared with progress_data
    Must start fresh.
    """
    UI(testing_mode = True).start()

if __name__ == "__main__":
    test_main()



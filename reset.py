"""Reset the app:
remove folders under projects
clear data.json
"""
import shutil
import json
import os

def reset():
    for folder in os.listdir("projects"):
        if not folder.startswith('.'):
            shutil.rmtree("projects/" + folder)

    data_file = open("data.json", "w")
    json.dump({}, data_file)
    data_file.close()

if __name__ == "__main__":
    reset()
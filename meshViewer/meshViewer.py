#!/usr/bin/python3

import argparse
import json
import os
import subprocess

def getSetupFileOutput():
    #On windows this would be something different, which is why I made it a function.
    return "/tmp/avSetup.cfg"

def produceSetupFile():
    data = {}
    data["Project"] = "Mesh Viewer"
    data["CompositorBackground"] = "1 0 1 1"
    data["SquirrelEntryFile"] = "main.nut"
    data["DataDirectory"] = "/home/edward/Documents/avTools/meshViewer/squirrel/"

    with open(getSetupFileOutput(), 'w') as outfile:
        json.dump(data, outfile)

def main():
    helpText = '''A tool to inspect ogre meshes in the avEngine.
    This python script is responsible for creating a temporary engine project,
    containing the necessary resource locations and settings to produce the correct editor window.
    '''

    parser = argparse.ArgumentParser(description = helpText)

    parser.add_argument('resoucePath', metavar='I', type=str, nargs='?', help='Either a mesh file or avSetup.cfg file.')

    args = parser.parse_args()

    produceSetupFile()

    devnull = open(os.devnull, 'w')
    process = subprocess.Popen(["/home/edward/Documents/avEngine/build/av", "/tmp/avSetup.cfg"], stdout=devnull, stderr=devnull)
    devnull.close()


if __name__ == "__main__":
    main()

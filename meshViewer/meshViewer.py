#!/usr/bin/python3

import argparse
import json
import os
import subprocess
from pathlib import Path

def getSetupFileOutput():
    #On windows this would be something different, which is why I made it a function.
    return "/tmp/avSetup.cfg"

def produceSetupFile(meshPath):
    resourceLocations = []
    targetMesh = ""

    objectPath = Path(meshPath)
    if(not objectPath.exists()):
        print("Provided mesh path does not exist.")
        return False
    if(not objectPath.is_file()):
        print("Please provide a path to a file.")
        return False

    if(objectPath.is_absolute()):
        resourceLocations.append(objectPath.parent)
        targetMesh = objectPath.name

    data = {}
    data["Project"] = "Mesh Viewer"
    data["CompositorBackground"] = "1 0 1 1"
    data["SquirrelEntryFile"] = "main.nut"
    data["DataDirectory"] = "/home/edward/Documents/avTools/meshViewer/squirrel/"
    data["OgreResourcesFile"] = "/tmp/OgreResources.cfg"
    data["UserSettings"] = {
        "targetMesh" : targetMesh
    }

    with open(getSetupFileOutput(), 'w') as outfile:
        json.dump(data, outfile)

    #TODO temporary. In future I'm going to use the avSetup file resource locations.
    with open("/tmp/OgreResources.cfg", 'w') as outfile:
        outfile.write('[General]\n')
        for i in resourceLocations:
            outfile.write('FileSystem=' + str(i))

    return True

def main():
    helpText = '''A tool to inspect ogre meshes in the avEngine.
    This python script is responsible for creating a temporary engine project,
    containing the necessary resource locations and settings to produce the correct editor window.
    '''

    parser = argparse.ArgumentParser(description = helpText)

    parser.add_argument('resourcePath', metavar='I', type=str, nargs='?', help='Either a mesh file or avSetup.cfg file.')

    args = parser.parse_args()

    targetPath = args.resourcePath
    if(targetPath is None):
        print("Please provide a path to a mesh or avSetup.cfg file")
        return

    result = produceSetupFile(targetPath)
    if(not result):
        return

    devnull = open(os.devnull, 'w')
    process = subprocess.Popen(["/home/edward/Documents/avEngine/build/av", "/tmp/avSetup.cfg"], stdout=devnull, stderr=devnull)
    devnull.close()


if __name__ == "__main__":
    main()

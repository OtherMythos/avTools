#!/usr/bin/python3

import argparse
import json
import os
import subprocess
from pathlib import Path
import shutil
import tempfile

def getTmpPath():
    return tempfile.gettempdir()

def getSetupFileOutput():
    path = getTmpPath()
    return str(Path(path) / "avSetup.cfg")

def getOgresResourcesFileOutput():
    path = getTmpPath()
    return str(Path(path) / "OgreResources.cfg")

def getExpectedToolsPath():
    return str(Path.home() / "Documents/avTools/")

def getExpectedEnginePath():
    enginePath = Path.home() / "Documents/avEngine/"
    if os.name == "nt": #Windows
        enginePath = enginePath / "build/Debug/av.exe"
    else:
        enginePath = enginePath / "build/av"

    return str(enginePath)

'''
Create a directory somewhere temporary which will behave as the current working directory.
This is to make sure the hlms shaders or other ogre stuff ends up somewhere other than one of the user's directories.
'''
def getTemporaryCWD():

    target = Path(getTmpPath()) / "meshViewer"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir()

    return target

def produceSetupFile(meshPath):
    resourceLocations = []
    targetMesh = ""

    objectPath = Path(meshPath)
    if(not objectPath.exists()):
        print("Provided mesh path does not exist.")
        return ""
    if(not objectPath.is_file()):
        print("Please provide a path to a file.")
        return ""

    objectPath = objectPath.resolve()
    assert objectPath.exists()

    resourceLocations.append(objectPath.parent)
    targetMesh = objectPath.name

    ogreResourcesFile = getOgresResourcesFileOutput()
    expectedToolsPath = getExpectedToolsPath()
    finalToolsPath = Path(expectedToolsPath) / "meshViewer/squirrel/"
    if not finalToolsPath.exists() or not finalToolsPath.is_dir():
        print("No valid path to the avTools directory. Checked %s" % str(finalToolsPath))
        return ""
    print("Squirrel files found at path: %s" % finalToolsPath)

    data = {}
    data["Project"] = "Mesh Viewer"
    data["CompositorBackground"] = "0.156 0.184 0.215 1"
    data["SquirrelEntryFile"] = "main.nut"
    data["DataDirectory"] = str(finalToolsPath)
    data["OgreResourcesFile"] = ogreResourcesFile
    data["NumWorkerThreads"] = 1 #The minimum number
    data["UserSettings"] = {
        "targetMesh" : targetMesh
    }
    data["DynamicPhysics"] = {
        "disabled" : True
    }

    outFilePath = getSetupFileOutput()
    print("Writing avSetup.cfg file to %s" % outFilePath)
    with open(outFilePath, 'w') as outfile:
        json.dump(data, outfile)

    with open(ogreResourcesFile, 'w') as outfile:
        outfile.write('[General]\n')
        for i in resourceLocations:
            outfile.write('FileSystem=' + str(i))

    return outFilePath

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

    targetResultPath = produceSetupFile(targetPath)
    if(not targetResultPath):
        return


    targetCWD = getTemporaryCWD()
    devnull = open(os.devnull, 'w')

    enginePath = getExpectedEnginePath()

    process = subprocess.Popen([enginePath, targetResultPath], stdout=devnull, stderr=devnull, cwd=str(targetCWD))
    devnull.close()


if __name__ == "__main__":
    main()

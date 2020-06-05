#!/usr/bin/python3

#Converts avSetup.cfg files from a given location recursively.
#The files were originally a .cfg type, but they've now been updated to a json format.

import os
import sys
from pathlib import Path
import configparser
import json

def convertFile(filePath):
    targetPath = Path(filePath)
    if(targetPath.name != "avSetup.cfg"):
        return

    print("Converting %s" % targetPath)
    config = configparser.ConfigParser()
    # config.read(targetPath)
    # print(config)

    config_string = ""
    #I have to modify the file slightly.
    #The config parser library forces you to have a header for each value, so I add a dummy here.
    #You also can't have tabs as a deliminator, so I replace those with equals.
    with open(filePath, 'r') as f:
        config_string = '[NullSection]\n' + f.read()
        config_string = config_string.replace("\t", "=")

    contentsDict = {}

    config = configparser.ConfigParser()
    config.optionxform = lambda option: option #This is required to keep the case for some reason.
    config.read_string(config_string)
    for each_section in config.sections():
        for (each_key, each_val) in config.items(each_section):
            #print(each_key)
            #print(each_val)

            if(each_val.isdigit()):
                each_val = int(each_val)
            elif(each_val.upper() == "true".upper()):
                each_val = True
            elif(each_val.upper() == "false".upper()):
                each_val = False
            elif(each_val.replace('.', '').isdigit()):
                each_val = float(each_val)

            if not each_section in contentsDict:
                contentsDict[each_section] = []
            contentsDict[each_section].append( (each_key, each_val) )


    jsonData = {}
    for i in contentsDict["NullSection"]:
        jsonData[i[0]] = i[1]

    print(contentsDict)
    for key, value in contentsDict.items():
        if(key == "NullSection"):
            continue
        if(not "UserSettings" in jsonData):
            jsonData["UserSettings"] = {}
        if(not key in jsonData["UserSettings"]):
            jsonData["UserSettings"][key] = {}
        for secondKey, secondValue in value:
            jsonData["UserSettings"][key][secondKey] = secondValue

    json_data = json.dumps(jsonData, indent=4)
    print(json_data)

    os.remove(filePath)
    writeFile = open(filePath, "a")
    writeFile.write(json_data)
    writeFile.close()


def recursiveConvert(dirPath):
    for root, subdirs, files in os.walk(dirPath):
        for i in files:
            #print("\t%s" % i)
            targetPath = os.path.join(root, i)
            if(os.path.isdir(targetPath)):
                recursiveConvert(targetPath)
                continue

            #Should be a file by this point
            convertFile(targetPath)
            #parsedNamespace = parseSingleFile(targetPath)

            # if(parsedNamespace.valid()):
            #     printNamespaceDescription(parsedNamespace)
            #     foundNamespaces.append(parsedNamespace)

def __main__():
    if(len(sys.argv) <= 1):
        print("Please provide a path to a directory containing setup files")
        return

    targetPath = Path(sys.argv[1])
    if(not targetPath.exists() or not targetPath.is_dir()):
        print("Invaid path. Please provide a path to a directory")
        return

    recursiveConvert(targetPath)

__main__()

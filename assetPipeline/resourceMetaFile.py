import os
from pathlib import Path
import json

'''
Defines a single piece of data for building a resource.
'''
class ResourceEntrySettings:

    def __init__(self):
        self.outDir = ""
        self.width = None
        self.height = None
        self.widthDiv = 1
        self.heightDiv = 1
        self.ignore = False

'''
Defines data per directory for resources.
This data can be specified by profile, allowing greater control over the outputted resources.
'''
class ResourceMetaFile:

    def __init__(self):
        self.parsedProfileGroups = {}

    def parseFile(self, path):
        filePath = Path(path)
        if not filePath.exists() or not filePath.is_file():
            return False

        with open(path) as file:
            data = json.load(file)
            self.parseJsonData(data)

        return True

    def parseJsonString(self, string):
        data = json.loads(string)
        return self.parseJsonData(data)

    def parseJsonData(self, data):
        for i in data:
            groupData = {}
            for y in data[i]:
                groupData[y] = self.parseProfileData(data[i][y])
            self.parsedProfileGroups[i] = groupData

        return True

    def parseProfileData(self, data):
        parsedSettings = ResourceEntrySettings()

        if "outDir" in data and type(data["outDir"]) is str:
            parsedSettings.outDir = data["outDir"]
        if "width" in data and type(data["width"]) is int:
            parsedSettings.width = data["width"]
        if "height" in data and type(data["height"]) is int:
            parsedSettings.height = data["height"]
        if "widthDiv" in data and type(data["widthDiv"]) is int:
            parsedSettings.widthDiv = data["widthDiv"]
        if "heightDiv" in data and type(data["heightDiv"]) is int:
            parsedSettings.heightDiv = data["heightDiv"]
        if "ignore" in data and type(data["ignore"]) is bool:
            parsedSettings.ignore = data["ignore"]

        return parsedSettings

    '''
    Validate that the resourceMetaBase file contains the appropriate profiles to support this meta file.
    Assumes the meta file was correctly parsed.
    Returns true or false depending on the success.
    '''
    def validateAgainstProfiles(self, baseFile):
        for i in self.parsedProfileGroups:
            result = baseFile.containsProfile(i)
            if result is not True:
                print("resourceMeta file defines unknown profile %s" % i)
                return False

        return True


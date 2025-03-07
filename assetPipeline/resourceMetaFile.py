import os
from pathlib import Path
import json

'''
Defines a single piece of data for building a resource.
'''
class ResourceEntrySettings:

    def __init__(self):
        self.settings = {}

    '''
    Apply the settings of a ResourceEntry to this one.
    '''
    def applySettings(self, target):
        self.settings.update(target)

    def __getitem__(self, key):
        return self.settings.get(key, None)

    def __getattr__(self, key):
        return self.settings.get(key, None)

    def __setattr__(self, key, value):
        if key == "settings":  # Prevent infinite recursion in __init__
            super().__setattr__(key, value)
        else:
            self.settings[key] = value


'''
Defines data per directory for resources.
This data can be specified by profile, allowing greater control over the outputted resources.
'''
class ResourceMetaFile:

    def __init__(self):
        self.parsedProfileGroups = {}
        self.parsedResources = {}

    def parseFile(self, path):
        print(path)
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

    def getProfilesForResource(self, resName):
        if resName in self.parsedResources:
            return self.parsedResources[resName]
        return None

    def parseJsonData(self, data):
        for i in data:
            groupData = {}
            for y in data[i]:
                groupData[y] = self.parseProfileData(data[i][y])
                self.addProfileToParsedResource(y, i)
            self.parsedProfileGroups[i] = groupData

        return True

    def determineResSettingsForProfile(self, profile, resource):
        return self.parsedProfileGroups[profile][resource]

    def determineResourceEntrySettings(self, baseFile, resName, targetProfile):
        if not resName in self.parsedResources:
            return ResourceEntrySettings()

        targetResources = self.parsedResources[resName]
        if type(targetResources) is str:
            return self.determineResSettingsForProfile(targetResources, resName)

        #From here on we need to process a list of resource settings.
        assert(type(targetResources) is list)
        returnedArray = baseFile.getProfileOrderForArray(targetResources)
        if returnedArray is None:
            return ResourceEntrySettings()
        '''
        Go through this list. Get the settings for that object at the lowest profile.
        Go all the way through to get the final value.
        '''
        assert len(returnedArray) > 0
        print(self.parsedProfileGroups)
        newReturnSettings = ResourceEntrySettings()
        for i in returnedArray:
            assert i in self.parsedProfileGroups
            targetGroup = self.parsedProfileGroups[i]
            assert resName in targetGroup
            targetResourceSettings = targetGroup[resName]
            newReturnSettings.applySettings(targetResourceSettings.settings)
            if targetProfile == i:
                #Stop building from here
                break

        return newReturnSettings

    '''
    Insert settings for a parsed resource into the parsedResources map.
    If only one profile is registered this will be stored as just a plain string.
    If not it will be stored as an array containing multiple values.
    '''
    def addProfileToParsedResource(self, resName, groupName):
        if(resName in self.parsedResources):
            if type(self.parsedResources[resName]) is str:
                self.parsedResources[resName] = [self.parsedResources[resName], groupName]
            else:
                self.parsedResources[resName].append(groupName)
        else:
            self.parsedResources[resName] = groupName

    def parseProfileData(self, data):
        parsedSettings = ResourceEntrySettings()
        parsedSettings.applySettings(data)

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


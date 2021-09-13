import os
from pathlib import Path
import json

#TODO parse this file at the beginning of the execution.
#Ensure the universal is there.
#Write the other files.

'''
Data for a profile.
A profile might be something like MacOS, IOS, Desktop, etc.
Profiles allow the user to specify a target build for resources.
For instance, building lower resolution textures on mobile devices.
'''
class ProfileEntry:

    def __init__(self):
        self.name = ""
        self.parent = None
        self.children = []
        self.independantBuildable = False


'''
Encapsulate the functionality of a resourceMetaBase file.
This is a file type which contains base information about the resources to be parsed.
'''
class ResourceMetaBase:

    def __init__(self):
        self.profiles = []
        self.defaultProfile = "Universal"

    def parseFile(self, path):
        filePath = Path(path)
        if not filePath.exists() or not filePath.is_file():
            return False

        with open(path) as file:
            data = json.load(file)
            if not self.parseJsonData(data):
                return False

        return True

    def parseJsonString(self, string):
        data = json.loads(string)
        return self.parseJsonData(data)

    def _containsUniversalProfile(self, profiles):
        for i in range(len(self.profiles)):
            if self.profiles[i].name == "Universal":
                return i

        return None

    def parseJsonData(self, data):
        self.profiles.clear()

        if "profiles" in data:
            profileData = data["profiles"]
            for i in profileData:
                newProfile = ProfileEntry()
                newProfile.name = i
                curr = profileData[i]
                if "ChildOf" in curr and type(curr["ChildOf"]) is str:
                    #Universal can't be a child of anything.
                    if i == "Universal":
                        continue
                    newProfile.parent = curr["ChildOf"]
                if "IndependantBuildable" in curr and type(curr["IndependantBuildable"]) is bool:
                    newProfile.independantBuildable = curr["IndependantBuildable"]

                self.profiles.append(newProfile)

        #Make sure the list contains a universal entry.
        universalIndex = self._containsUniversalProfile(self.profiles)
        if universalIndex is None:
            universalProfile = ProfileEntry()
            universalProfile.name = "Universal"
            universalProfile.parent = None
            universalProfile.independantBuildable = True
            self.profiles.append(universalProfile)

        #Scan through all the found profiles and match up the parents with the children.
        for i in range(len(self.profiles)):
            currentProfile = self.profiles[i]
            parent = currentProfile.parent
            if parent is None:
                #Only universal should have a parent of None.
                assert currentProfile.name == "Universal"
                continue
            #Loop through and find that parent.
            found = False
            for y in range(len(self.profiles)):
                targetProfile = self.profiles[y]
                if targetProfile.name == parent:
                    targetProfile.children.append(currentProfile.name)
                    found = True
                    break
            if not found:
                print("Could not find parent %s for profile %s" % (currentProfile.parent, currentProfile.name))
                return False


        #Read other values
        if "DefaultProfile" in data and type(data["DefaultProfile"]) is str:
            default = data["DefaultProfile"]
            self.defaultProfile = default

        return True


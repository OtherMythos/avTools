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
        self.independantBuildable = True
        self.parentIndex = -1
        self.id = -1



'''
Encapsulate the functionality of a resourceMetaBase file.
This is a file type which contains base information about the resources to be parsed.
'''
class ResourceMetaBase:

    def __init__(self):
        self.valid = False;
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

        return self._processParsedJSON()

    def parseJsonString(self, string):
        data = json.loads(string)
        successValue = self.parseJsonData(data)
        if not successValue:
            return False

        if not self._processParsedJSON():
            return False

        return True

    def _processParsedJSON(self):
        #Validate the values.
        defaultValid = self.isDefaultProfileValid()
        if defaultValid is False:
            print("The default profile (%s) is not valid" % self.defaultProfile)
            return False

        self.valid = True;
        return True

    def getProfileIdx(self, name):
        for i in range(len(self.profiles)):
            if self.profiles[i].name == name:
                return i
        return None

    '''
    Order the array relative to the profile order.
    For instance a list containing ["Desktop", "Universal"] would be ordered
    ["Universal", "Desktop"] assuming Desktop is a child of Universal.
    '''
    def getProfileOrderForArray(self, array):
        #Contain all the items in the new list.
        newList = []
        for i in array:
            newList.append( self.profiles[self.getProfileIdx(i)] )
        assert(len(newList) == len(array))
        newList.sort(key=lambda x: x.id, reverse=False)
        retList = []
        for i in newList:
            retList.append(i.name)

        return retList


    def containsProfile(self, name):
        idx = self.getProfileIdx(name);
        return idx is not None

    def _containsUniversalProfile(self):
        return self.containsProfile("Universal")

    def isDefaultProfileValid(self):
        idx = self.getProfileIdx(self.defaultProfile);
        if idx == None:
            return False
        prof = self.profiles[idx]
        if not prof.independantBuildable:
            return False

        return True

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

                newProfile.id = len(self.profiles)
                self.profiles.append(newProfile)

        #Make sure the list contains a universal entry.
        universalIndex = self._containsUniversalProfile()
        if universalIndex is False:
            universalProfile = ProfileEntry()
            universalProfile.name = "Universal"
            universalProfile.parent = None
            universalProfile.independantBuildable = True
            newProfile.id = len(self.profiles)
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

        #Loop through and determine the relative parent id for each profile.
        #This is used later on to determine the priority different profiles have over each other.
        for i in range(len(self.profiles)):
            currentProfile = self.profiles[i]
            if currentProfile.name == "Universal":
                currentProfile.parentIndex = 0
                continue
            targetParent = currentProfile.parent
            idCount = 0
            while targetParent is not None:
                foundProfile = self.profiles[self.getProfileIdx(targetParent)]
                targetParent = foundProfile.parent
                idCount+=1
            currentProfile.parentIndex = idCount


        #Read other values
        if "DefaultProfile" in data and type(data["DefaultProfile"]) is str:
            default = data["DefaultProfile"]
            self.defaultProfile = default

        return True


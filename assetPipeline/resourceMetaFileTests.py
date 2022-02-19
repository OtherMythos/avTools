import unittest
from pathlib import Path

from resourceMetaFile import *
from resourceMetaBase import *

class ParsedFileTests(unittest.TestCase):

    def test_parseFileSettings(self):
        jsonData = '''
        {
            "Universal":{
                "Grass.png": {
                    "outDir": "something.png",
                    "width": 100,
                    "height": 100,
                    "widthDiv": 2,
                    "heightDiv": 2
                },
                "Rocks.png": {
                    "outDir": "other.png",
                    "ignore": true
                }
            },
            "Desktop":{
                "other.jpg": {
                }
            }
        }
        '''
        f = ResourceMetaFile()
        result = f.parseJsonString(jsonData)
        self.assertTrue(result)

        self.assertEqual(len(f.parsedProfileGroups), 2)
        self.assertTrue("Universal" in f.parsedProfileGroups)

        targetGroup = f.parsedProfileGroups["Universal"]
        self.assertEqual(len(targetGroup), 2)
        self.assertTrue("Grass.png" in targetGroup)
        self.assertTrue("Rocks.png" in targetGroup)

        self.assertEqual(targetGroup["Rocks.png"].outDir, "other.png")
        #Should be the default values from now on.
        self.assertEqual(targetGroup["Rocks.png"].width, None)
        self.assertEqual(targetGroup["Rocks.png"].height, None)
        self.assertEqual(targetGroup["Rocks.png"].widthDiv, 1)
        self.assertEqual(targetGroup["Rocks.png"].heightDiv, 1)
        self.assertEqual(targetGroup["Rocks.png"].ignore, True)

        self.assertEqual(targetGroup["Grass.png"].outDir, "something.png")
        self.assertEqual(targetGroup["Grass.png"].width, 100)
        self.assertEqual(targetGroup["Grass.png"].height, 100)
        self.assertEqual(targetGroup["Grass.png"].widthDiv, 2)
        self.assertEqual(targetGroup["Grass.png"].heightDiv, 2)
        self.assertEqual(targetGroup["Grass.png"].ignore, False)

        #Now check the other profile.
        targetGroup = f.parsedProfileGroups["Desktop"]
        self.assertEqual(len(targetGroup), 1)
        self.assertTrue("other.jpg" in targetGroup)

        #Should all just be defaults
        self.assertEqual(targetGroup["other.jpg"].outDir, "")
        self.assertEqual(targetGroup["other.jpg"].width, None)
        self.assertEqual(targetGroup["other.jpg"].height, None)
        self.assertEqual(targetGroup["other.jpg"].widthDiv, 1)
        self.assertEqual(targetGroup["other.jpg"].heightDiv, 1)
        self.assertEqual(targetGroup["other.jpg"].ignore, False)

        self.assertEqual(f.parsedResources["Grass.png"], "Universal")
        self.assertEqual(f.parsedResources["Rocks.png"], "Universal")
        self.assertEqual(f.parsedResources["other.jpg"], "Desktop")

    def test_parseFileInMultipleProfiles(self):
        jsonData = '''
        {
            "Universal":{
                "Grass.png": {
                    "outDir": "something.png"
                },
                "Rocks.png": {
                    "outDir": "somethingElse.png"
                }
            },
            "Desktop":{
                "Grass.png": {
                    "outDir": "somethingElse.png"
                }
            },
            "Other":{
                "Grass.png": {
                    "outDir": "somethingElse.png"
                }
            }
        }
        '''
        f = ResourceMetaFile()
        result = f.parseJsonString(jsonData)
        self.assertTrue(result)

        self.assertEqual(len(f.parsedProfileGroups), 3)

        self.assertEqual(f.parsedResources["Grass.png"], ["Universal", "Desktop", "Other"])
        self.assertEqual(f.parsedResources["Rocks.png"], "Universal")

    def test_determineResourceEntrySettings_failsWithMissingProfile(self):
        #Mentions profile other which doesn't exist.
        jsonData = '''
        {
            "Universal":{
                "Grass.png": {
                    "outDir": "something.png"
                },
                "Rocks.png": {
                    "outDir": "somethingElse.png"
                }
            },
            "Desktop":{
                "Grass.png": {
                    "outDir": "somethingElse.png"
                }
            },
            "Other":{
                "Grass.png": {
                    "outDir": "somethingElse.png"
                }
            }
        }
        '''
        f = ResourceMetaFile()
        result = f.parseJsonString(jsonData)
        self.assertTrue(result)
        #Parse the meta base.
        jsonData = '''
        {
            "profiles":{
            "Universal": {"IndependantBuildable":true}
        },
        "DefaultProfile": "Universal"
        }
        '''
        b = ResourceMetaBase()
        result = b.parseJsonString(jsonData)

    def test_determineResourceEntrySettings(self):
        jsonData = '''
        {
            "Universal":{
                "Grass.png": {
                    "outDir": "something.png"
                },
                "Rocks.png": {
                    "outDir": "somethingElse.png"
                }
            },
            "Desktop":{
                "Grass.png": {
                    "outDir": "somethingElse.png"
                }
            },
            "Other":{
                "Grass.png": {
                    "outDir": "somethingOther.png",
                    "width": 2,
                    "height": 3,
                    "widthDiv": 4,
                    "heightDiv": 5,
                    "ignore": true
                }
            },
            "Inherits":{
                "Grass.png": {
                    "outDir": "inherited.png"
                }
            }
        }
        '''

        f = ResourceMetaFile()
        result = f.parseJsonString(jsonData)
        self.assertTrue(result)
        #Parse the meta base.
        jsonData = '''
        {
            "profiles":{
            "Universal": {"IndependantBuildable":true},
            "Desktop": {"ChildOf":"Universal"},
            "Linux": {"ChildOf":"Desktop"},
            "Other": {"ChildOf":"Linux"},
            "Inherits": {"ChildOf":"Other"},
            "MacOS": {"ChildOf":"Desktop"},
            "Windows": {"ChildOf":"Linux"},
            "SomethingElse": {"ChildOf":"Windows"}
        },
        "DefaultProfile": "Universal"
        }
        '''
        b = ResourceMetaBase()
        result = b.parseJsonString(jsonData)

        settings = f.determineResourceEntrySettings(b, "Grass.png", "Desktop")
        self.assertEqual(settings.outDir, "somethingElse.png")
        self.assertEqual(settings.width, None)
        self.assertEqual(settings.height, None)
        self.assertEqual(settings.widthDiv, 1)
        self.assertEqual(settings.heightDiv, 1)
        self.assertEqual(settings.ignore, False)

        settings = f.determineResourceEntrySettings(b, "Grass.png", "Other")
        self.assertEqual(settings.outDir, "somethingOther.png")
        self.assertEqual(settings.width, 2)
        self.assertEqual(settings.height, 3)
        self.assertEqual(settings.widthDiv, 4)
        self.assertEqual(settings.heightDiv, 5)
        self.assertEqual(settings.ignore, True)

        #Here values should be inherited from the previous set.
        settings = f.determineResourceEntrySettings(b, "Grass.png", "Inherits")
        self.assertEqual(settings.outDir, "inherited.png")
        self.assertEqual(settings.width, 2)
        self.assertEqual(settings.height, 3)
        self.assertEqual(settings.widthDiv, 4)
        self.assertEqual(settings.heightDiv, 5)
        self.assertEqual(settings.ignore, True)

        settings = f.determineResourceEntrySettings(b, "Grass.png", "Universal")
        self.assertEqual(settings.outDir, "something.png")
        self.assertEqual(settings.width, None)
        self.assertEqual(settings.height, None)
        self.assertEqual(settings.widthDiv, 1)
        self.assertEqual(settings.heightDiv, 1)
        self.assertEqual(settings.ignore, False)

        settings = f.determineResourceEntrySettings(b, "Rocks.png", "Universal")
        self.assertEqual(settings.outDir, "somethingElse.png")
        self.assertEqual(settings.width, None)
        self.assertEqual(settings.height, None)
        self.assertEqual(settings.widthDiv, 1)
        self.assertEqual(settings.heightDiv, 1)
        self.assertEqual(settings.ignore, False)


    def test_validateMetaFileProfiles(self):
        jsonData = '''
        {
            "Universal":{
            },
            "Something":{
            },
            "Desktop":{
            }
        }
        '''
        f = ResourceMetaFile()
        result = f.parseJsonString(jsonData)
        self.assertTrue(result)

        #Parse the meta base file.
        jsonData = '''
        {
            "profiles":{
                "Universal": {"IndependantBuildable":false},
                "Desktop": {"ChildOf":"Universal"}
            },
            "DefaultProfile": "Desktop"
        }
        '''
        baseFile = ResourceMetaBase()
        result = baseFile.parseJsonString(jsonData)
        self.assertTrue(result)

        result = f.validateAgainstProfiles(baseFile)
        self.assertFalse(result)

        ## New data
        jsonData = '''
        {
            "Universal":{
            },
            "Desktop":{
            }
        }
        '''
        f = ResourceMetaFile()
        result = f.parseJsonString(jsonData)
        self.assertTrue(result)

        result = f.validateAgainstProfiles(baseFile)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()

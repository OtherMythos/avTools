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
            "DefaultProfile": "Universal"
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
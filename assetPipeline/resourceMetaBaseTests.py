import unittest
from pathlib import Path

from resourceMetaBase import *

class ParsedFileTests(unittest.TestCase):

    def test_parseProfiles(self):
        jsonData = '''
        {
            "profiles":{
                "Universal": {"IndependantBuildable":false},
                "Desktop": {"ChildOf":"Universal"}
            },
            "DefaultProfile": "Universal"
        }
        '''
        f = ResourceMetaBase()
        result = f.parseJsonString(jsonData)
        self.assertTrue(result)
        self.assertEqual(len(f.profiles), 2)

        self.assertEqual(f.profiles[0].name, "Universal")
        self.assertFalse(f.profiles[0].independantBuildable)
        self.assertIsNone(f.profiles[0].parent)
        self.assertEqual(len(f.profiles[0].children), 1)
        self.assertEqual(f.profiles[0].children[0], "Desktop")
        self.assertEqual(f.profiles[0].parentIndex, 0)

        self.assertEqual(f.profiles[1].name, "Desktop")
        self.assertEqual(f.profiles[1].parent, "Universal")
        self.assertEqual(len(f.profiles[1].children), 0)
        self.assertEqual(f.profiles[1].parentIndex, 1)

    def test_parseParentProfiles(self):
        jsonData = '''
        {
            "profiles":{
                "Universal": {"IndependantBuildable":false},
                "Desktop": {"ChildOf":"Universal"},
                "Linux": {"ChildOf":"Desktop"},
                "MacOS": {"ChildOf":"Desktop"},
                "Windows": {"ChildOf":"Linux"},
                "SomethingElse": {"ChildOf":"Windows"}
            },
            "DefaultProfile": "Universal"
        }
        '''
        f = ResourceMetaBase()
        result = f.parseJsonString(jsonData)
        self.assertTrue(result)
        self.assertEqual(len(f.profiles), 6)

        self.assertEqual(f.profiles[0].parentIndex, 0)
        self.assertEqual(f.profiles[1].parentIndex, 1)
        self.assertEqual(f.profiles[2].parentIndex, 2)
        self.assertEqual(f.profiles[3].parentIndex, 2)
        self.assertEqual(f.profiles[4].parentIndex, 3)
        self.assertEqual(f.profiles[5].parentIndex, 4)

    def test_parseProfilesCreatesUniversalProfile(self):
        jsonData = '''
        {
            "profiles":{
                "Desktop": {"ChildOf":"Universal"}
            },
            "DefaultProfile": "Universal"
        }
        '''
        f = ResourceMetaBase()
        result = f.parseJsonString(jsonData)
        self.assertTrue(result)
        self.assertEqual(len(f.profiles), 2)

        self.assertEqual(f.profiles[0].name, "Desktop")
        self.assertEqual(f.profiles[0].parent, "Universal")
        self.assertEqual(len(f.profiles[0].children), 0)

        self.assertEqual(f.profiles[1].name, "Universal")
        self.assertTrue(f.profiles[1].independantBuildable)
        self.assertIsNone(f.profiles[1].parent)
        self.assertEqual(len(f.profiles[1].children), 1)

    def test_parseProfilesCreatesUniversalProfile(self):
        jsonData = '''
        {
            "profiles":{
                "Desktop": {"ChildOf":"dfsdfkjsdlkfsdjkl"}
            },
            "DefaultProfile": "Universal"
        }
        '''
        f = ResourceMetaBase()
        result = f.parseJsonString(jsonData)
        self.assertFalse(result)
        self.assertEqual(len(f.profiles), 2)

    def test_getProfileOrderForArray(self):
        jsonData = '''
        {
            "profiles":{
                "Desktop": {"ChildOf":"Universal"},
                "Linux": {"ChildOf":"Desktop"},
                "Other": {"ChildOf":"Linux"},
                "OtherSecond": {"ChildOf":"Other"},

                "FirstChild": {"ChildOf":"Desktop"},
                "SecondChild": {"ChildOf":"Linux"}
            },
            "DefaultProfile": "Universal"
        }
        '''
        f = ResourceMetaBase()
        result = f.parseJsonString(jsonData)
        self.assertTrue(result)

        result = f.getProfileOrderForArray(["Linux", "Desktop", "Universal"])
        self.assertEqual(result, ["Universal", "Desktop", "Linux"])

        result = f.getProfileOrderForArray(["Other", "OtherSecond", "Linux", "Desktop", "Universal"])
        self.assertEqual(result, ["Universal", "Desktop", "Linux", "Other", "OtherSecond"])

        result = f.getProfileOrderForArray(["FirstChild", "SecondChild", "Linux", "Desktop", "Universal"])
        self.assertEqual(result, ["Universal", "Desktop", "Linux", "FirstChild", "SecondChild"])


if __name__ == '__main__':
    unittest.main()
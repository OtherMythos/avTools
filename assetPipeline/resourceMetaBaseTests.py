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

        self.assertEqual(f.profiles[1].name, "Desktop")
        self.assertEqual(f.profiles[1].parent, "Universal")
        self.assertEqual(len(f.profiles[1].children), 0)

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


if __name__ == '__main__':
    unittest.main()
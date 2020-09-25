import unittest
from pathlib import Path
from FileParser import ParsedFile

class ParsedFileTests(unittest.TestCase):

    def test_readValuesFromGroup(self):
        return
        f = ParsedFile(Path("test"))
        f.fileContent = ["@name something", "something more@desc description", "*/"]
        result = f.readValuesFromGroup("")
        self.assertIn("name", result)
        self.assertIn("desc", result)

        self.assertEqual(result["name"], "something\nsomething more")
        self.assertEqual(result["desc"], "description\n")


    def test_readValuesFromGroupMalformedAt(self):
        f = ParsedFile(Path("test"))
        f.fileContent = ["@name@something@else", "This is something else", "Some more text*/"]
        result = f.readValuesFromGroup("")
        #This should fail because of the malformed ints.
        self.assertEqual(result, {})
        self.assertNotEqual(f.failureReason, '')

    def test_parseParamInfo(self):
        f = ParsedFile(Path(""))
        #Due to the way these are parsed sometimes there's surplus characters.
        result = f.parseParamInfo("param1:mapName:A")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["type"], "mapName")
        self.assertEqual(result["surplus"], "A")

        #Not providing a type.
        result = f.parseParamInfo("param1:something")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["surplus"], "something")
        self.assertIsNone(result["type"])

        #Trimming the surplus
        result = f.parseParamInfo("param2:      something")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 2)
        self.assertEqual(result["surplus"], "something")
        self.assertIsNone(result["type"])

        #Large param numbers
        result = f.parseParamInfo("param11:String: something")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 11)
        self.assertEqual(result["surplus"], "something")
        self.assertEqual(result["type"], "String")

    def test_parseParamInfoReturnsNoneWithInvalidInput(self):
        f = ParsedFile(Path(""))
        values = [
            "param1:fjfdjkajk:::::jdfskljldsa",
            "param:fjfdjkajk:jdfskljldsa",
            "param1:fjfdjkajk:jdfskljldsa::",
            "param1::something"
        ]
        for i in values:
            result = f.parseParamInfo(i)
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
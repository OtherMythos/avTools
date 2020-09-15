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


if __name__ == '__main__':
    unittest.main()
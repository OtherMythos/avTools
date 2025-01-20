from pathlib import Path

import os
import json

class DirectoryTimestampFile:

    def __init__(self):
        self.timestampEntries = {}

    def parseFile(self, path):
        filePath = Path(path)
        if not filePath.exists() or not filePath.is_file():
            return False

        with open(path) as file:
            self.timestampEntries = json.load(file)

        return True

    def timestampRequiresBuild(self, path, fullPath):
        if path in self.timestampEntries:
            if self._getTimestampFromFile(fullPath) <= self.timestampEntries[path]:
                return False

        return True

    def _getTimestampFromFile(self, path):
        return os.path.getmtime(path)

    def touchFile(self, fileName, fullPath):
        timestamp = self._getTimestampFromFile(fullPath)
        self.timestampEntries[fileName] = timestamp

    def write(self, fullPath):
        try:
            with open(fullPath, "w") as file:
                json.dump(self.timestampEntries, file, indent=4)
        except Exception as e:
            print(f"Unable to write timestamp file to path {fullPath}")
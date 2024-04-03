class TestProjectEntry:
    def __init__(self, name):
        self.name = name
        self.path = ""
        self.recursive = False
        self.baseSetupFile = None

    def setPath(self, path, configPath):
        self.path = configPath.absolute().parent / path


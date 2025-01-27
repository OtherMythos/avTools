import os
import shutil

class Settings:
    def __init__(self, inputDir, outputDir, blenderPath, targetProfile, linkFiles, modules, rebuild):
        self.blenderPath = blenderPath
        self.inputDir = inputDir
        self.outputDir = outputDir
        self.targetProfile = targetProfile
        self.linkFiles = linkFiles
        self.modules = modules
        self.rebuild = rebuild

    def blenderExecutableValid(self):
        if os.path.isfile(self.blenderPath):
            return True
        if shutil.which(self.blenderPath) is not None:
            return True

        return False

from assetModules.AssetModule import *

from pathlib import Path
import subprocess

class AssetModuleBlend(AssetModule):
    def __init__(self, settings):
        super().__init__(settings)

        self.extension = ".blend"

        self.blenderExportFile = "/scripts/blenderExporter/exportTest.py"

        self.checkFiles()

    def checkFiles(self):
        #TODO there's a bug here if not in a same directory as this file.
        self.blenderExportFileExists = Path(self.blenderExportFile).exists()

    def exportForFile(self, filePath):
        outputTargetDirectory = self.prepareOutputDirectoryForFile(filePath)
        self.exportBlenderFile(filePath, outputTargetDirectory)

    def exportBlenderFile(self, filePath, outputPath):
        if not self.blenderExportFileExists:
            print("Blender export file at path %s does not exist" % self.blenderExportFile)
            return
        print("exporting blender file at path '%s' to directory '%s'" % (filePath, outputPath))

        #./blender -b ~/Documents/meshTests/newMesh/Grave.blend --python ~/Documents/avTools/exportTest.py -- /tmp/3
        devnull = open(os.devnull, 'w')
        paths = [str(self.settings.blenderPath), "-b", str(filePath), "--python", self.blenderExportFile, "--", str(outputPath)]
        #print(' '.join(paths))
        process = subprocess.Popen(paths, stdout=devnull, stderr=devnull)
        process.wait()
        #print(process.communicate())
        devnull.close()
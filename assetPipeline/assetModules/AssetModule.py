import os
import shutil

'''
Base class logic to describe how to export an asset type.
Asset types register a file ending such as .txt, .png, .svg, etc.
'''
class AssetModule:
    def __init__(self, settings):
        self.extension = None
        self.settings = settings

    def getExtension(self):
        return self.extension

    def exportForFile(self, filePath, resSettings):
        print("Example module exporting file %s" % filePath)

    '''
    When it's time to write an output file from the input, check the output directory contains the correct structure, similar to the input.
    If it does not, create the appropriate directory structure.
    '''
    def prepareOutputDirectoryForFile(self, inputFilePath, includeFileName = False):
        relativePath = inputFilePath.relative_to(self.settings.inputDir)
        outputTargetPath = self.settings.outputDir/ relativePath

        #Just the parent directory, without the file name.
        parentPath = outputTargetPath.parents[0]
        if not parentPath.exists():
            parentPath.mkdir(parents=True)

        if includeFileName:
            parentPath = parentPath / inputFilePath.name

        return parentPath

    def copyFile(self, filePath, resSettings):
        outPath = filePath
        if resSettings.outDir != "":
            outPath = rootPath / resSettings.outDir
        outputTarget = self.prepareOutputDirectoryForFile(outPath, True)

        if self.settings.linkFiles:
            os.symlink(filePath, outputTarget)
            print("symlinked %s to %s" % (filePath, outputTarget))
        else:
            shutil.copyfile(filePath, outputTarget)
            print("copied %s to %s" % (filePath, outputTarget))
import os
import shutil

'''
Base class logic to describe how to export an asset type.
Asset types register a file ending such as .txt, .png, .svg, etc.
'''
class AssetModule:
    def __init__(self):
        self.extension = None

    def getExtension(self):
        return self.extension

    def exportForFile(self, filePath, inputDirectory, outputPath):
        print("Example module exporting file %s to %s" % (filePath, outputPath))

    '''
    When it's time to write an output file from the input, check the output directory contains the correct structure, similar to the input.
    If it does not, create the appropriate directory structure.
    '''
    def prepareOutputDirectoryForFile(self, inputFilePath, inputDirectory, outputDirectory, includeFileName = False):
        relativePath = inputFilePath.relative_to(inputDirectory)
        outputTargetPath = outputDirectory / relativePath

        #Just the parent directory, without the file name.
        parentPath = outputTargetPath.parents[0]
        if not parentPath.exists():
            parentPath.mkdir(parents=True)

        if includeFileName:
            parentPath = parentPath / inputFilePath.name

        return parentPath

    def copyFile(self, filePath, inputDir, outputDir, resSettings):
        outPath = filePath
        if resSettings.outDir != "":
            outPath = rootPath / resSettings.outDir
        outputTarget = self.prepareOutputDirectoryForFile(outPath, inputDir, outputDir, True)

        # relPath = filePath.relative_to(outputTarget)
        # print(str(relPath))

        #TODO return the ability to symlink files.
        #if self.linkFiles:
        if False:
            os.symlink(filePath, outputTarget)
            print("symlinked %s to %s" % (filePath, outputTarget))
        else:
            shutil.copyfile(filePath, outputTarget)
            print("copied %s to %s" % (filePath, outputTarget))
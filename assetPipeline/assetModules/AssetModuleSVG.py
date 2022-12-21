from assetModules.AssetModule import *

from cairosvg import svg2png

class AssetModuleSVG(AssetModule):
    def __init__(self):
        self.extension = ".svg"

    def exportForFile(self, filePath, inputDirectory, outputDirectory):
        retPath = filePath.with_suffix(".png")
        outputTarget = self.prepareOutputDirectoryForFile(retPath, inputDirectory, outputDirectory, True)

        svg2png(url=str(filePath),write_to=str(outputTarget))
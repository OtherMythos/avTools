#!/usr/bin/python3

import os
import shutil
import random

targetPath = os.getcwd() + "/"
mapName = "map"

chunkStartX = -10
chunkStartY = -10
chunkEndX = 10
chunkEndY = 10

meshesNum = 2

def createMapDirectory():
    if(os.path.isdir(targetPath + mapName)):
        shutil.rmtree(targetPath + mapName)

    try:
        os.mkdir(targetPath + mapName)
    except OSError:
        print("Creation of the directory %s failed" % path)

def createChunkDirectory(x, y):
    baseDir = targetPath + mapName + "/"
    dirName = ""

    xVal = x
    if(x < 0):
        dirName += '-'
        xVal *= -1
    dirName += str(xVal).zfill(4)

    yVal = y
    if(y < 0):
        dirName += '-'
        yVal *= -1
    dirName += str(yVal).zfill(4)

    dirPath = baseDir + dirName
    try:
        os.mkdir(dirPath)
    except OSError:
        print("Creation of the directory %s failed" % dirName)

    fillChunkDirectory(dirPath)

def fillChunkDirectory(path):
    createMeshesFile(path + "/meshes.txt")

def createMeshesFile(filePath):
    file = open(filePath, "w")

    file.write(str(meshesNum) + "\n")

    for i in range(meshesNum):
        nums = []
        for y in range(3):
            ammount = 100
            if(y == 1): ammount = 10
            nums.append("{:.4f}".format(random.random() * ammount))
        for z in range(3):
            nums.append("{:.4f}".format(random.random()))
        print(nums)
        file.write("ogrehead2\n")
        file.write(nums[0] + " " + nums[1] + " " + nums[2] + "\n")
        file.write(nums[3] + " " + nums[4] + " " + nums[5] + "\n")

    file.close()

def fillChunks():
    for y in range(chunkStartY, chunkEndY):
        for x in range(chunkStartX, chunkEndX):
            createChunkDirectory(x, y)

def __main__():
    createMapDirectory()
    fillChunks()

__main__()

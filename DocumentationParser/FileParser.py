import os
import sys
from pathlib import Path
from enum import Enum

'''
Abstracts the logic for parsing a single file.
This class will collect all the data and namespaces found within the file.
'''
class ParsedFile:
    '''
    What type of object is currently being parsed.
    '''
    class ParseType(Enum):
        NONE = 0
        NAMESPACE = 1

    SQNAMESPACE = "/**SQNamespace"
    SQTERMINATOR = "*/"

    SQNAMESPACE_NAME = "name"
    SQNAMESPACE_DESCRIPTION = "desc"

    def __init__(self, path):
        self.filePath = path
        self.currentLine = -1 # Start at -1 so the first readLine reads 0
        self.fileEnd = False
        self.fileContent = None
        self.failureReason = ""
        self.foundValues = {}

    def parse(self):

        with open(self.filePath, 'r') as f:
            self.fileContent = f.readlines()
            self._parse()

            f.close()

        print("found " + str(self.foundValues))

    def _parse(self):
        while not self.fileEnd:
            line = self.readLine()

            if self.SQNAMESPACE in line:
                print(line)
                self.parseNamespaceType()

        #return self.ParseType.NONE

    def parseNamespaceType(self):
        line = self.getCurrentLine()
        assert self.SQNAMESPACE in line
        startPos = line.find(self.SQNAMESPACE)
        startLine = line[startPos:]
        print(startLine)

        values = self.readValuesFromGroup(startLine)

        if not self.SQNAMESPACE_NAME in values or not self.SQNAMESPACE_DESCRIPTION in values:
            return

        foundNamespace = {
            self.SQNAMESPACE_NAME:values[self.SQNAMESPACE_NAME],
            self.SQNAMESPACE_DESCRIPTION:values[self.SQNAMESPACE_DESCRIPTION],
        }

        if "namespaces" not in self.foundValues:
            self.foundValues["namespaces"] = []
        self.foundValues["namespaces"].append(foundNamespace)

    '''
    Read in the values from a number of lines and produce a dictionary of keys and their values found within this list.
    '''
    def readValuesFromGroup(self, startLine):
        currentParse = "none"
        parsingContent = True

        returnedVals = {}
        def writeToVals(state, value):
            if not state in returnedVals:
                returnedVals[state] = ""
            returnedVals[state] += value.rstrip()

        currentLine = startLine
        while(parsingContent):
            if self.SQTERMINATOR in currentLine:
                idx = currentLine.find(self.SQTERMINATOR)
                currentLine = currentLine[:idx]
                #Stop parsing after this line is done with.
                parsingContent = False

            if "@" in currentLine:
                #This line contains 1 or more changes to the state. In this case loop through each character and check it.
                workingLine = currentLine
                currentLineParse = currentParse
                currentIdx = 0
                for i in currentLine:
                    if i == '@':
                        #Take whatever was before the @ and commit it.
                        prevContent = workingLine[:currentIdx]
                        writeToVals(currentLineParse, prevContent)

                        workingLine = workingLine[currentIdx:]
                        #What if this finds the end of the file?
                        spaceIdx = workingLine.find(" ")
                        if spaceIdx == -1:
                            #No space was found, meaning the @ was malformed.
                            self.failureReason = "Malformed @ description."
                            return {}
                        #1 to strip away the @ symbol.
                        currentLineParse = workingLine[1:spaceIdx]
                        #+1 to not include the space
                        workingLine = workingLine[spaceIdx+1:]

                        currentIdx = 0

                    currentIdx += 1

                #Write whatever we have left to our current parser state.
                if workingLine != '':
                    writeToVals(currentLineParse, workingLine + '\n')
                #Set whatever the current parsing type is.
                currentParse = currentLineParse

            else:
                #There is no change to the current parser state, so just write into the list.
                if currentLine != '':
                    writeToVals(currentParse, currentLine + '\n')


            if not parsingContent:
                #Don't go past here if the terminator value was found.
                continue
            currentLine = self.readLine()
            if self.fileEnd:
                parsingContent = False

        return returnedVals

    def getCurrentLine(self):
        assert self.currentLine < len(self.fileContent)
        return self.fileContent[self.currentLine]

    def readLine(self):
        self.currentLine+=1
        if(self.currentLine >= len(self.fileContent)):
            self.fileEnd = True
            return ""
        return self.fileContent[self.currentLine]


'''
A class to manage the parsing of files and their contents.
Reads through files in the provided directory, filling containers with the data it finds.
'''
class FileParser:
    def __init__(self):
        pass
        self.foundData = {}

    def parseFiles(self, path):
        for root, subdirs, files in os.walk(path):
            print("-- %s" % root)
            for i in files:
                print("\t%s" % i)
                targetPath = Path(root) / i
                assert not targetPath.is_dir()

                if targetPath.suffix != ".cpp" and targetPath.suffix != ".h":
                    continue


                file = ParsedFile(targetPath)
                file.parse()

                #Commit what was found to the file parser list.
                self.mergeFoundValues(file)

        #print("FOUND " + str(self.foundData))

    def mergeFoundValues(self, parsedFile):
        for i in parsedFile.foundValues:
            if not i in self.foundData:
                self.foundData[i] = parsedFile.foundValues[i]
                continue
            self.foundData[i] += parsedFile.foundValues[i]


'''
class ParsedEntry:
    name = ""
    returnDescription = ""
    description = ""
    parameters = [("", "")] * 9

class NamespaceEntry:
    name = ""
    description = ""
    functions = []

    def valid(self):
        return (self.name != "")

    def parseNamespace(self, content, currentLine):

        targetLine = currentLine
        running = True
        while(running):
            if(targetLine >= len(content)):
                running = False
                break

            line = content[targetLine]
            if("*/" in line):
                running = False
                break
            if("@name" in line):
                self.name = parseNamespaceName(line)
            if("@desc" in line):
                self.description = parseNamespaceDescription(line)

            targetLine += 1

def parseFiles(path):
    foundNamespaces = []

    for root, subdirs, files in os.walk(path):
        print('-- ' + root)
        #list_file_path = os.path.join(root, 'my-directory-list.txt')
        #print('list_file_path = ' + list_file_path)
        for i in files:
            print("\t%s" % i)
            targetPath = os.path.join(root, i)
            if(os.path.isdir(targetPath)):
                continue
            parsedPath = Path(targetPath)
            if parsedPath.suffix != ".cpp" or parsedPath.suffix != ".h":
                continue

            parsedNamespace = parseSingleFile(targetPath)

            if(parsedNamespace.valid()):
                printNamespaceDescription(parsedNamespace)
                foundNamespaces.append(parsedNamespace)

    return foundNamespaces

def parseSingleFile(path):
    namespace = NamespaceEntry()
    namespace.functions = []

    with open(path, 'r') as f:
        content = f.readlines()
        currentLine = 0
        for i in content:
            if("/**SQFunction" in i):
                result = beginParsingContent(content, currentLine)
                namespace.functions.append(result)

            if("/**SQNamespace" in i):
                namespace.parseNamespace(content, currentLine)

            currentLine += 1

        f.close()

    return namespace


def parseNamespaceDescription(line):
    return line[line.find("@desc"):].replace("@desc", '').lstrip().strip('\n')

def parseNamespaceName(line):
    return line[line.find("@name"):].replace("@name", '').lstrip().strip('\n')

def parseName(startLine, content):
    outString = content[startLine]

    return outString.replace("@name", '').lstrip().strip('\n')

def parseReturn(startLine, content):
    outString = content[startLine]

    return outString.replace("@returns", '').lstrip().strip('\n')

def parseDescription(startLine, content):
    outString = content[startLine]

    return outString.replace("@desc", '').lstrip().strip('\n')

def parseParameter(startLine, content):
    line = content[startLine]
    prev = line[line.find("@param"):].replace("@param", '').lstrip().strip('\n')
    #The first character should be the target parameter.
    targetNum = int(prev[0])

    varName = ""
    #return targetNum, prev[1:].lstrip()
    retVal = prev[1:].lstrip()
    if(retVal[0] == ":"):
        #A parameter name is being passed.
        retVal = retVal[1:]
        foundIdx = retVal.find(":")
        if(foundIdx != -1): #If it's -1 the other value wasnt found.
            varName = retVal[:foundIdx]
            retVal = retVal[foundIdx+1:] #Remove the :
            retVal = retVal.lstrip()

    return [targetNum, retVal, varName]

def beginParsingContent(content, currentLine):
    entry = ParsedEntry()
    entry.parameters = [("", "")] * 9

    for i in range(currentLine, len(content)):
        line = content[i]
        if("@name" in line):
            entry.name = parseName(i, content)

        if("@returns" in line):
            entry.returnDescription = parseReturn(i, content)

        if("@desc" in line):
            entry.description = parseDescription(i, content)

        if("@param" in line):
            outValue = parseParameter(i, content)
            targetParam = outValue[0]
            desc = outValue[1]
            varName = outValue[2]
            entry.parameters[targetParam] = (desc, varName)

        if("*/" in line):
            break #We're done parsing this definition.

    return entry

def printNamespaceDescription(namespace):
    print("\t\t" + namespace.name)

    for i in namespace.functions:
        print("\t\t\tname: " + i.name)
        print("\t\t\treturns: " + i.returnDescription)
        print("\t\t\tdescription: " + i.description)

        current = 0
        for y in i.parameters:
            if y[0]:
                print("\t\t\tparam%i: %s" % (current, y))
            current += 1
        print("")
'''
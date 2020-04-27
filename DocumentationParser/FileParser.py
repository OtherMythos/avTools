import os
import sys

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
        currentLine = 0;
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

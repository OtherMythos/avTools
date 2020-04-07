import os
import sys

class ParsedEntry:
    name = ""
    returnDescription = ""
    description = ""
    parameters = [""] * 9

def parseFiles(path):
    for root, subdirs, files in os.walk(path):
        print('-- ' + root)
        #list_file_path = os.path.join(root, 'my-directory-list.txt')
        #print('list_file_path = ' + list_file_path)
        for i in files:
            print("\t%s" % i)
            targetPath = os.path.join(root, i)
            if(os.path.isdir(targetPath)):
                continue

            parseSingleFile(targetPath)

def parseSingleFile(path):
    foundNamespace = ""
    foundFunctions = []

    with open(path, 'r') as f:
        content = f.readlines()
        currentLine = 0;
        for i in content:
            if("SQFunction" in i):
                result = beginParsingContent(content, currentLine)
                foundFunctions.append(result)

            if("SQNamespace" in i):
                foundNamespace = parseNamespace(i)

            currentLine += 1

        f.close()

    if(foundNamespace and foundFunctions):
        printNamespaceDescription(foundNamespace, foundFunctions)

def parseNamespace(line):
    return line[line.find("SQNamespace"):].replace("SQNamespace", '').lstrip().strip('\n')

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

    return targetNum, prev[1:].lstrip()

def beginParsingContent(content, currentLine):
    entry = ParsedEntry()

    for i in range(currentLine, len(content)):
        line = content[i]
        if("@name" in line):
            entry.name = parseName(i, content)

        if("@returns" in line):
            entry.returnDescription = parseReturn(i, content)

        if("@desc" in line):
            entry.description = parseDescription(i, content)

        if("@param" in line):
            targetParam, desc = parseParameter(i, content)
            entry.parameters[targetParam] = desc

        if("*/" in line):
            break #We're done parsing this definition.

    return entry

def printNamespaceDescription(name, functions):
    print("\t\t" + name)

    for i in functions:
        print("\t\t\tname: " + i.name)
        print("\t\t\treturns: " + i.returnDescription)
        print("\t\t\tdescription: " + i.description)

        current = 0
        for y in i.parameters:
            if y:
                print("\t\t\tparam%i: %s" % (current, y))
            current += 1
        print("")

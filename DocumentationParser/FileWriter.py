
'''
A class responsible for writing found data to disk in an rst format.
'''
class FileWriter:

    def __init__(self, foundData):
        self.foundData = foundData

    def writeFileText(self, file, namespace):
        file.write(namespace["name"] + "\n")
        file.write("=" * len(namespace["name"]) + "\n\n")
        file.write(namespace["desc"] + "\n\n")

        self.writeFunctionText(file, namespace)
        self.writeConstantText(file, namespace)

    def writeConstantText(self, file, namespace):
        writtenHeader = False
        for i in self.foundData["constants"]:
            if i["namespace"] is None:
                continue
            if i["namespace"] != namespace["name"]:
                continue
            if not writtenHeader:
                file.write("Constants\n^^^^^^^^^\n")
                writtenHeader = True

            functionDef = "**" + i["name"] + "**"
            if "desc" in i:
                functionDef += " - " + i["desc"]
            functionDef += "\n\n"

            file.write(functionDef)

    def writeFunctionText(self, file, namespace):
        writtenHeader = False
        for i in self.foundData["functions"]:
            if i["namespace"] is None:
                continue
            if i["namespace"] != namespace["name"]:
                continue

            if not writtenHeader:
                file.write("API\n^^^\n")
                writtenHeader = True

            functionDef = ".. js:function:: "
            functionDef += i["name"]
            functionDef += "("

            addedValues = False
            if "params" in i:
                for y in i["params"]:
                    type = y["type"]
                    if(type != None):
                        addedValues = True
                        functionDef += str(type) + ", "
                        #functionDef += "#, "

            if(addedValues):
                #Remove the final , if this was the final entry
                functionDef = functionDef[:-2]
            functionDef += ")\n\n"
            file.write(functionDef)

            if addedValues:
                parameters = i["params"]
                for y in range(len(parameters)):
                    e = parameters[y]
                    if(e["type"] != None and e["desc"] != None):
                        file.write("\t:param "+e["type"]+": "+e["desc"]+"\n")


            if("returns" in i):
                file.write("\t:returns: " + i["returns"] + "\n\n")

            if "desc" in i:
                file.write("\t" + i["desc"] + "\n\n")
            else:
                file.write("\n")

    def writeIndexFile(self, filePath):
        print("Generating index file at: " + str(filePath))
        f = open(filePath, "w")

        f.write(
"""Squirrel API
============

This is the documentation for the squirrel api calls.

Function Namespaces
-------------------

.. toctree::
    :maxdepth: 1
    :name: toc-squirrl-functions

""")

        for i in self.foundData["namespaces"]:
            f.write("    " + i["name"] + ".rst\n")

        f.close()

    def writeRst(self, outDirectory):
        for i in self.foundData["namespaces"]:
            filePath = outDirectory / (i["name"] + ".rst")
            print(filePath)
            f = open(filePath, "w")
            self.writeFileText(f, i)
            f.close()

        indexFilePath = outDirectory / "index.rst"
        self.writeIndexFile(indexFilePath)

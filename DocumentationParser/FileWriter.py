
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

        file.write("API\n^^^\n")

        #TODO disabled for now.
        #Next time, include functions in the namespace writes to grab functions.
        return
        for i in namespace.functions:
            functionDef = ".. js:function:: "
            functionDef += i.name
            functionDef += "("

            addedValues = False
            for y in i.parameters:
                if(y[0] != ""):
                    addedValues = True
                    functionDef += y[1] + ", "
                    #functionDef += "#, "

            if(addedValues):
                #Remove the final , if this was the final entry
                functionDef = functionDef[:-2]
            functionDef += ")\n\n"
            file.write(functionDef)

            for y in range(len(i.parameters)):
                e = i.parameters[y]
                if(e[0] != "" and e[1] != ""):
                    file.write("\t:param "+e[1]+": "+e[0]+"\n")


            if(i.returnDescription):
                file.write("\t:returns: " + i.returnDescription + "\n\n")


            file.write("\t" + i.description + "\n\n")

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

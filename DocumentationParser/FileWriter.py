
def writeFileText(file, namespace):
    file.write(namespace.name + "\n")
    file.write("=" * len(namespace.name) + "\n\n")
    file.write(namespace.description + "\n\n")

    file.write("API\n^^^\n")

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

def writeIndexFile(filePath, namespaces):
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

    for i in namespaces:
        f.write("    " + i.name + ".rst\n")

    f.close()

def writeNamespacesRst(outDirectory, namespaces):
    for i in namespaces:
        filePath = outDirectory / (i.name + ".rst")
        print(filePath)
        f = open(filePath, "w")
        writeFileText(f, i)
        f.close()

    indexFilePath = outDirectory / "index.rst"
    writeIndexFile(indexFilePath, namespaces)

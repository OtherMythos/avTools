import bpy
import sys

import xml.etree.cElementTree as ET

def processCollection(idx, parent, col):
    elem = ET.SubElement(parent, "empty")

    for ob in col.objects:
        if ob.type != 'MESH':
            continue

        meshName = ob.data.name + ".mesh"
        meshElem = ET.SubElement(elem, "mesh", name=ob.name, mesh=meshName)
        posElem = ET.SubElement(meshElem, "position", x=str(ob.location[0]), y=str(ob.location[2]), z=str(-ob.location[1]))
        scaleElem = ET.SubElement(meshElem, "scale", x=str(ob.scale[0]), y=str(ob.scale[2]), z=str(ob.scale[1]))
        ob.rotation_mode = 'QUATERNION'
        #0(w) goes first, z(3) and y(2) are flipped.
        quaternionElem = ET.SubElement(meshElem, "orientation", x=str(ob.rotation_quaternion[1]), y=str(ob.rotation_quaternion[3]), z=str(-(ob.rotation_quaternion[2])), w=str(ob.rotation_quaternion[0]))

    for ob in col.children:
        assert type(ob) is bpy.types.Collection
        print("collection: " + ob.name)
        processCollection(idx + 1, elem, ob)

'''
This script is intended to be run by blender in background mode.
Make sure you have blender2ogre installed as a blender extension, and it is properly enabled and everything.

Read through all visible objects in the scene and export them as an avEngine scene format.
'''
def main():
    from io_ogre.ogre.mesh import dot_mesh
    from io_ogre.ogre.skeleton import dot_skeleton

    try:
        idx = sys.argv.index('--')
    except:
        print("Include the output path.")
        print("i.e 'blender -b file.blend --python ~/Documents/avTools/exportTest.py -- /tmp/outPath'")
        return

    if idx+1 >= len(sys.argv):
        print("Include the output path.")
        print("i.e 'blender -b file.blend --python ~/Documents/avTools/exportTest.py -- /tmp/outPath'")
        return

    outPath = sys.argv[idx+1]
    print(outPath)

    c = bpy.context.collection

    root = ET.Element("scene")
    processCollection(0, root, c)


    tree = ET.ElementTree(root)
    tree.write(outPath)


if __name__ == "__main__":
    main()

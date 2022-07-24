#!/bin/bash -xe

if [[ $(uname -m) == "aarch64" ]]; then
    ln -s /builder/OgreMeshToolArm /bin/OgreMeshTool
else
    ln -s /builder/OgreMeshToolx86 /bin/OgreMeshTool
fi

#Start this up so gimp can be used in the container.
Xvfb :99 -screen 0 640x480x8 -nolisten tcp &

cd /scripts/assetPipeline

./assetTool.py -b /usr/bin/blender $*

#chmod -R 777 /buildOutput


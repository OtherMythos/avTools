#!/bin/bash -xe

if [[ $(uname -m) == "aarch64" ]]; then
    ln -s /builder/OgreMeshToolArm /bin/OgreMeshTool
else
    ln -s /builder/OgreMeshToolx86 /bin/OgreMeshTool
fi

cd /scripts/assetPipeline

./assetTool.py -b /usr/bin/blender $*

#chmod -R 777 /buildOutput


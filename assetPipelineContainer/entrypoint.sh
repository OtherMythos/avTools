#!/bin/bash -xe

#Start this up so gimp can be used in the container.
Xvfb :99 -screen 0 640x480x8 -nolisten tcp &

cd /scripts/assetPipeline

./assetTool.py -b /usr/bin/blender /buildInput/ /buildOutput/

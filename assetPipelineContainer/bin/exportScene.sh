#!/bin/bash

#This script is intended to be run inside the avEngine asset builder container.

blender -b /buildInput --python /scripts/blenderExporter/exportScene.py -- /buildOutput/outScene.xml

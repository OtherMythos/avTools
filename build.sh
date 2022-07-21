#!/bin/bash

#Build the image.
docker build -t asset-builder-image -f Dockerfile .
docker tag asset-builder-image registry.gitlab.com/edherbert/avtools/asset-builder-image:latest

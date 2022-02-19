#!/bin/bash -xe

if [ -v ${1} ]; then
    echo "Please provide a path of where to build to."
    exit 1
fi
if [ -v ${2} ]; then
    echo "Please provide a path to the input blend file."
    exit 1
fi
echo "Input files ${2}"
echo "Building to ${1}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "Current script dir: ${SCRIPT_DIR}"

docker run -it --name asset-builder-container --rm \
    -v "$1:/buildOutput" \
    -v "$2:/buildInput" \
    -v "${SCRIPT_DIR}/..:/scripts" \
    --entrypoint '/scripts/assetPipelineContainer/bin/exportScene.sh' asset-builder-image


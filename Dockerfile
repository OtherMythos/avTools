FROM ubuntu:24.04

WORKDIR /builder

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY :99

RUN apt-get update && apt-get install -y \
    wget \
    python3 \
    python3-pip \
    blender \
    git \
    libxt-dev \
    libxaw7-dev \
    gimp \
    xvfb \
    python3-cairosvg

COPY assetPipelineContainer/entrypoint.sh /builder/entrypoint.sh
RUN chmod +x /builder/entrypoint.sh

RUN mkdir /scripts
RUN mkdir /output

COPY assetPipeline /scripts/assetPipeline
COPY blenderExporter /scripts/blenderExporter

RUN blender --version | awk '{print $2}' | awk -F. '{print $1 "." $2}' > /blenderVersion
RUN mkdir -p /root/.config/blender/$(cat /blenderVersion)/scripts/addons
RUN git clone https://github.com/OGRECave/blender2ogre.git /builder/blender2ogre
RUN ln -s /builder/blender2ogre/io_ogre/ /root/.config/blender/$(cat /blenderVersion)/scripts/addons

COPY assetPipelineContainer/bin/OgreMeshToolArm /builder/OgreMeshToolArm
COPY assetPipelineContainer/bin/OgreMeshToolx86 /builder/OgreMeshToolx86
#RUN ln -s /builder/OgreMeshTool /bin/OgreMeshTool

COPY assetPipelineContainer/installAddon.py /builder/installAddon.py
RUN blender -b -P /builder/installAddon.py
#RUN sed -i "/'OGRETOOLS_XML_CONVERTER' : 'OgreXMLConverter',/c\'OGRETOOLS_XML_CONVERTER' : '/builder/OgreMeshTool'," /builder/blender2ogre/io_ogre/config.py
RUN sed -i "/'SWAP_AXIS' : 'xyz'/c\    'SWAP_AXIS' : 'xz-y'," /builder/blender2ogre/io_ogre/config.py

ENTRYPOINT ["/builder/entrypoint.sh"]

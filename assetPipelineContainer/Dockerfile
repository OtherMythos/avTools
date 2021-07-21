FROM ubuntu:20.04

WORKDIR /builder

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY :99

RUN apt-get update && apt-get install -y \
    wget \
    python3 \
    blender \
    git \
    libxt-dev \
    libxaw7-dev \
    gimp \
    xvfb

COPY entrypoint.sh /builder/entrypoint.sh
RUN chmod +x /builder/entrypoint.sh

RUN mkdir /scripts
RUN mkdir /output

RUN mkdir -p /root/.config/blender/2.82/scripts/addons
RUN git clone https://github.com/OGRECave/blender2ogre.git /builder/blender2ogre
RUN ln -s /builder/blender2ogre/io_ogre/ /root/.config/blender/2.82/scripts/addons

COPY bin/OgreMeshTool /builder/OgreMeshTool
RUN ln -s /builder/OgreMeshTool /bin/OgreMeshTool

COPY installAddon.py /builder/installAddon.py
RUN blender -b -P /builder/installAddon.py
#RUN sed -i "/'OGRETOOLS_XML_CONVERTER' : 'OgreXMLConverter',/c\'OGRETOOLS_XML_CONVERTER' : '/builder/OgreMeshTool'," /builder/blender2ogre/io_ogre/config.py
RUN sed -i "/'SWAP_AXIS' : 'xyz'/c\    'SWAP_AXIS' : 'xz-y'," /builder/blender2ogre/io_ogre/config.py

ENTRYPOINT ["/builder/entrypoint.sh"]

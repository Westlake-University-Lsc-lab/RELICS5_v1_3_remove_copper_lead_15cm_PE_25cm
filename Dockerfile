FROM docker.1ms.run/rootproject/root:6.34.00-ubuntu24.04

# Labels (optional but good for metadata)
LABEL author="qidian2"
LABEL version="1.0"

# Set environment variables
ENV G4INSTALL=/opt/geant4
ENV G4DATA_DIR=$G4INSTALL/share/Geant4/data
ENV G4LIB_DIR=$G4INSTALL/lib
ENV PATH=$G4INSTALL/bin:$PATH
RUN echo $G4INSTALL/lib >> /etc/ld.so.conf && ldconfig
ENV G4GDMLROOT=$G4INSTALL

RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list.d/ubuntu.sources && \
    apt-get update && apt-get install -y openssh-server && \
    mkdir -p /run/sshd && \
    apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install dependencies and build Geant4
RUN apt-get update && apt-get install -y \
        libxerces-c-dev \
        libexpat1-dev \
        libxkbcommon-dev \
        libxkbfile-dev \
        qt6-base-dev \
        mesa-utils \
        libglu1-mesa-dev \
        freeglut3-dev \
        mesa-common-dev && \
        apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN cd /opt && \
    G4_VERSION=11.4.0 && \
    wget https://github.com/Geant4/geant4/archive/refs/tags/v${G4_VERSION}.tar.gz && \
    tar -xf v${G4_VERSION}.tar.gz && \
    mv geant4-${G4_VERSION} geant4-source && \
    mkdir -p geant4-build && \
    cd geant4-build && \
    cmake ../geant4-source \
        -DCMAKE_INSTALL_PREFIX=/opt/geant4 \
        -DGEANT4_BUILD_MULTITHREADED=ON \
        -DGEANT4_USE_GDML=ON \
        -DGEANT4_USE_SYSTEM_EXPAT=ON \
        -DGEANT4_USE_SYSTEM_XERCESC=ON \
        -DGEANT4_INSTALL_DATA=ON \
        -DGEANT4_INSTALL_EXAMPLES=OFF \
        -DGEANT4_USE_OPENGL_X11=OFF \
        -DGEANT4_USE_QT=ON \
        -DGEANT4_USE_XM=OFF \
        -DGEANT4_USE_RAYTRACER_X11=OFF && \
    make -j$(nproc) && \
    make install && \
    rm -rf /opt/v${G4_VERSION}.tar.gz /opt/geant4-source /opt/geant4-build

RUN apt-get update && \
    apt-get install -y jq moreutils tmux \
        libyaml-cpp-dev \
        python3-pip python3-numpy python3-pandas python3-matplotlib python3-tqdm python3-sklearn && \
    apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --break-system-packages h5py polars -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip cache purge

RUN echo "PATH=${PATH}" > /etc/environment && \
    echo "ROOTSYS=${ROOTSYS}" >> /etc/environment && \
    echo "PYTHONPATH=${PYTHONPATH}" >> /etc/environment && \
    echo "CLING_STANDARD_PCH=${CLING_STANDARD_PCH}" >> /etc/environment && \
    echo "G4INSTALL=${G4INSTALL}" >> /etc/environment && \
    echo "G4DATA_DIR=${G4DATA_DIR}" >> /etc/environment && \
    echo "G4LIB_DIR=${G4LIB_DIR}" >> /etc/environment && \
    echo "G4GDMLROOT=${G4GDMLROOT}" >> /etc/environment

EXPOSE 22
VOLUME /root
WORKDIR /root

# Set default command / entrypoint
CMD ["/usr/sbin/sshd","-D"]

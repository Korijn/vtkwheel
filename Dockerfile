FROM quay.io/pypa/manylinux1_x86_64 as build

WORKDIR /tmp
ENV PATH=/opt/python/cp36-cp36m/bin:$PATH
RUN yum -y install xz
RUN pip install cmake ninja

# LLVM
RUN wget -qO- http://releases.llvm.org/6.0.0/llvm-6.0.0.src.tar.xz | unxz -c - | tar x
RUN cd llvm-6.0.0.src && mkdir build && cd build \
    && cmake .. -GNinja \
        -DCMAKE_BUILD_TYPE=Release \
        -DLLVM_BUILD_LLVM_DYLIB=ON \
        -DLLVM_ENABLE_RTTI=ON \
        -DLLVM_INSTALL_UTILS=ON \
        -DLLVM_TARGETS_TO_BUILD:STRING=X86 \
    && ninja install

# osmesa
RUN wget -qO- https://mesa.freedesktop.org/archive/mesa-18.0.2.tar.gz | tar xz
RUN cd mesa-18.0.1 \
    && ./configure \
        --disable-xvmc \
        --disable-glx \
        --disable-dri \
        --disable-gbm \
        --with-dri-drivers= \
        --with-gallium-drivers=swrast \
        --enable-texture-float \
        --disable-egl \
        --with-platforms= \
        --enable-gallium-osmesa \
        --enable-llvm \
    && make -j4 && make install

FROM quay.io/pypa/manylinux1_x86_64

WORKDIR /io

ENV PATH=/opt/python/cp36-cp36m/bin:$PATH

# Python deps
RUN pip install pipenv --upgrade
COPY ./Pipfile .
RUN pipenv install --dev --system --skip-lock

# TODO: copy built osmesa and llvm from build stage

# Build VTK
COPY ./build_vtk.py .
RUN python build_vtk.py --osmesa

# Build package
COPY ./setup_utils.py .
COPY ./setup.py .
RUN HAS_OSMESA=1 python setup.py bdist_wheel

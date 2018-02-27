FROM quay.io/pypa/manylinux1_x86_64

WORKDIR /io
VOLUME /io/dist

ENV PATH=/opt/python/cp36-cp36m/bin:$PATH
RUN pip install pipenv --upgrade

COPY ./Pipfile .
RUN pipenv install --dev --system --skip-lock

RUN yum install -y libXt-devel mesa-libGL-devel
COPY ./build_vtk.py .
RUN python build_vtk.py

COPY ./setup_utils.py .
COPY ./setup.py .
COPY ./Dockerfile_entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
CMD ./entrypoint.sh

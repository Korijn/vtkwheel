FROM ubuntu:16.04

WORKDIR /build

RUN apt-get update && sudo apt-get install -y \
        python3.6 \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.6 

COPY ./Pipfile .


COPY ./vtk .
COPY ./setup.py .


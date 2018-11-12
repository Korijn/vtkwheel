# Instructions

To make a wheel for Linux, I recommend using docker:

```
docker build . -t vtkwheel:manylinux1_x86_64_cp36
docker run --rm -v $(pwd)/dist:/io/dist vtkwheel:manylinux1_x86_64_cp36
```

To build locally:

```
pipenv install --dev
pipenv run python build_vtk.py
pipenv run python setup.py bdist_wheel
```

If you're building on Windows, make sure to run from a vanilla CPython 3.6 install and have the VS2017 build tools installed.

Note that the build_vtk.py script will overwrite ninja.exe and cmake.exe in your virtualenv, since the version on pypi are not compatible.

Note on auditwheel and delocate: these tools dont work 

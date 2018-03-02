# Instructions

To make a wheel that is manylinux1 compliant, I recommend using Docker:

```
docker build . -t vtkwheel:manylinux1_x86_64_cp36
docker run --rm -v $(pwd)/dist:/io/dist vtkwheel:manylinux1_x86_64_cp36
```

To run on your own system, run the following:

```
pipenv install --dev
pipenv run python build_vtk.py
pipenv run python setup.py bdist_wheel
pipenv run auditwheel repair ./dist/VTK* -w ./dist/repaired
```

On macOS instead of last line:

```
pipenv run delocate-wheel -v -w ./dist/repaired ./dist/VTK*
```

If you're building on Windows, make sure to run from a vanilla CPython 3.6 install and have the VS2017 build tools installed.

Note that the build_vtk.py script will overwrite ninja.exe and cmake.exe in your virtualenv, since the version on pypi are not compatible.

Also, I think there is no auditwheel-like tool for Windows. But then again, it is also less important on Windows.

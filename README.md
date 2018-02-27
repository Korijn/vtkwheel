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

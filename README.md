# Instructions

```
pipenv install --dev
pipenv run python build_vtk.py
pipenv run python setup.py bdist_wheel
```

Works for Linux!

Auditwheel doesn't like it yet.

```
RuntimeError: Invalid binary wheel, found shared library "libvtkChartsCore-8.1.so" in purelib folder.
The wheel has to be platlib compliant in order to be repaired by auditwheel.
```
set -ex
python setup.py bdist_wheel
auditwheel repair ./dist/VTK* -w ./dist/repaired

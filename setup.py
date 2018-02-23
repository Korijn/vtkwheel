from collections import defaultdict
from distutils.command.build import build as BuildCommand
from os.path import isfile, relpath, dirname
from os import unlink
from shutil import rmtree, copytree
from setuptools import setup
from setuptools.dist import Distribution
from glob import iglob


def get_data_files(build_dir="build_vtk", site_package_dir="vtk", bin_dir="bin", include_dir="include"):
    """
    data_files is a sequence of (directory, files) pairs.

    Each (directory, files) pair in the sequence specifies the installation directory 
    and the files to install there. If directory is a relative path, it is interpreted 
    relative to the installation prefix (Python’s sys.prefix for pure-Python packages, 
    sys.exec_prefix for packages that contain extension modules). Each file name in 
    files is interpreted relative to the setup.py script at the top of the package 
    source distribution. No directory information from files is used to determine 
    the final location of the installed file; only the name of the file is used.
    """
    isfile_filter = lambda path: isfile(path)
    # executables
    bin_files = list(filter(isfile_filter, iglob(f"{build_dir}/{bin_dir}/**/*", recursive=True)))
    # headers
    include_files = list(filter(isfile_filter, iglob(f"{build_dir}/{include_dir}/**/*", recursive=True)))

    # construct data_files datastructure
    data_files = defaultdict(list)
    for filename in bin_files + include_files:
        target_dir = relpath(dirname(filename), build_dir)
        data_files[target_dir].append(filename)

    # convert defaultdict to plain list of tuples of lists
    # >>> a = {}
    # >>> a['foo'] = [1, 2, 3]
    # >>> a['bar'] = [7, 2]
    # >>> a.items()
    # dict_items([('foo', [1, 2, 3]), ('bar', [7, 2])])
    # >>> list(a.items())
    # [('foo', [1, 2, 3]), ('bar', [7, 2])]
    return list(data_files.items())


class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True


setup(
    name='VTK',
    version='8.1.0',
    description='VTK is an open-source toolkit for 3D computer graphics, image processing, and visualization',
    author='VTK Community',
    url='https://www.vtk.org',
    package_dir={'': 'build_vtk'},
    packages=['vtk'],
    include_package_data=True,
    data_files=get_data_files(),
    distclass=BinaryDistribution,
)

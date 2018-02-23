from collections import defaultdict
from distutils.command.build import build as BuildCommand
from os.path import isfile, relpath, dirname, splitext
from os import unlink
from shutil import rmtree, copytree
from setuptools import setup, find_packages
from setuptools.dist import Distribution
from glob import iglob


def get_package_data(build_dir="build_vtk", package_dir="vtk"):
    """
    The package_data argument is a dictionary that maps from package names to lists of glob patterns
    """
    isfile_filter = lambda path: isfile(path)
    notpyfile_filter = lambda path: splitext(path)[-1] not in {'.py', '.pyc'}
    # non-python files
    package_files = list(filter(notpyfile_filter, filter(isfile_filter, iglob(f"{build_dir}/{package_dir}/**/*", recursive=True))))

    file_list = []
    for filename in package_files:
        rel_filename = relpath(filename, f"{build_dir}/{package_dir}")
        file_list.append(rel_filename)

    return {package_dir: file_list}


def get_data_files(build_dir="build_vtk", bin_dir="bin", include_dir="include"):
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
    package_data=get_package_data(),
    packages=find_packages('build_vtk'),
    include_package_data=True,
    data_files=get_data_files(),
    distclass=BinaryDistribution,
)

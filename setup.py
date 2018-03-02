from setup_utils import BinaryDistribution, get_data_files, get_package_data

from setuptools import setup, find_packages

import sys

is_win = (sys.platform == 'win32')


build_dir = 'build_vtk'

if is_win:
    data_dirs = ["Scripts", "include", "lib/cmake"]
    site_packages_dir = f"{build_dir}/Lib/site-packages"
else:
    data_dirs = ["bin", "include", "lib/cmake"]
    site_packages_dir = f"{build_dir}/lib/python{sys.version_info[0]}.{sys.version_info[1]}/site-packages"

package_dir = {'': site_packages_dir}
packages = find_packages(site_packages_dir)


setup(
    name='VTK',
    version='8.1.0',
    description='VTK is an open-source toolkit for 3D computer graphics, image processing, and visualization',
    author='VTK Community',
    url='https://www.vtk.org',
    package_dir=package_dir,
    package_data=get_package_data(packages, package_dir=package_dir),
    packages=packages,
    include_package_data=True,
    data_files=get_data_files(build_dir, ["bin", "include", "lib/cmake"]),
    distclass=BinaryDistribution,
)

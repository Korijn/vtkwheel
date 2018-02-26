from setup_utils import BinaryDistribution, get_data_files, get_package_data

from setuptools import setup, find_packages


root_package_dir = 'build_vtk'
package_dir = {'': root_package_dir}
packages = find_packages(root_package_dir)

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
    data_files=get_data_files(root_package_dir),
    distclass=BinaryDistribution,
)

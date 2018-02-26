from itertools import chain
from collections import defaultdict
from distutils.command.build import build as BuildCommand
from os.path import isfile, relpath, dirname, splitext
from os import unlink
from shutil import rmtree, copytree
from setuptools import setup, find_packages
from setuptools.dist import Distribution
from glob import iglob


class BinaryDistribution(Distribution):
    """
    Specialized setuptools `Distribution` class that forces a platform-specific package build.

    In the scenario that you are not providing any Extensions to the ext_modules keyword argument of `setup()`, but 
    would still like to build a platform-specific wheel, you can provide this class to the `distclass` keyword 
    argument of `setup()`. Setuptools will then recognize your distribution as containing Extensions and build a
    platform-specific wheel.

    Examples
    --------
    >>> setup(distclass=BinaryDistribution)
    """

    def has_ext_modules(self):
        return True


def get_package_dir(self, package, package_dir=None):
    """
    Return the directory, relative to the top of the source distribution, where package 'package' should be found
    (at least according to the 'package_dir' option, if any).

    Notes
    -----
    Copied and modified source from distutils.command.build_py
    """
    if package_dir is None:
        package_dir = {}
    
    path = package.split('.')

    if not package_dir:
        if path:
            return os.path.join(*path)
        else:
            return ''
    else:
        tail = []
        while path:
            try:
                pdir = package_dir['.'.join(path)]
            except KeyError:
                tail.insert(0, path[-1])
                del path[-1]
            else:
                tail.insert(0, pdir)
                return os.path.join(*tail)
        else:
            # Oops, got all the way through 'path' without finding a
            # match in package_dir.  If package_dir defines a directory
            # for the root (nameless) package, then fallback on it;
            # otherwise, we might as well have not consulted
            # package_dir at all, as we just use the directory implied
            # by 'tail' (which should be the same as the original value
            # of 'path' at this point).
            pdir = package_dir.get('')
            if pdir is not None:
                tail.insert(0, pdir)

            if tail:
                return os.path.join(*tail)
            else:
                return ''


def get_package_data(packages, exclude=('.py', '.pyc'), package_dir=None):
    """
    Parameters
    ----------
    packages : iterable of str
        List of packages to collect files for
    exclude : iterable of str
        List of file extensions to exclude
    package_dir : mapping of str -> str
        Same as `package_dir` argument to `setup()`
    
    Returns
    -------
    mapping of str -> list of str
        `package_data` argument to `setup()`
    """
    dir_filter = lambda path: isfile(path)
    exclude_set = set(exclude)  # convert to set for more efficient lookup time
    exclude_filter = lambda path: splitext(path)[-1] not in exclude_set

    package_data = defaultdict(list)
    for package in packages:
        package_path = get_package_dir(package, package_dir=package_dir)
        for filename in filter(exclude_filter, filter(dir_filter, iglob(f"{package_path}/*"))):
            rel_filename = relpath(filename, package_path)
            package_data[package].append(rel_filename)

    return package_data


def get_data_files(prefix, bin_path="bin", include_path="include"):
    """
    Parameters
    ----------
    prefix : str
        All other parameters and returned values are relative to this path prefix
    bin_path : str
        Path relative to `prefix` containing binaries
    include_path : str
        Path relative to `prefix` containing headers

    Returns
    -------
    sequence of (directory, files) pairs.
        `data_files` argument to `setup()`
    """
    dir_filter = lambda path: isfile(path)
    bin_files = filter(dir_filter, iglob(f"{prefix}/{bin_dir}/**/*", recursive=True))
    include_files = filter(dir_filter, iglob(f"{prefix}/{include_dir}/**/*", recursive=True))

    data_files = defaultdict(list)
    for filename in chain.from_iterable([bin_files, include_files]):
        target_dir = relpath(dirname(filename), prefix)
        data_files[target_dir].append(filename)

    return list(data_files.items())

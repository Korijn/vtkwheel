import subprocess
import os
import sys


is_win = (sys.platform == 'win32')
is_darwin = (sys.platform == 'darwin')


def clone_vtk(branch="v8.1.0", dir="src/vtk"):
    """Shallow-clone of VTK gitlab repo of tip of `branch` to `dir`."""
    if os.path.exists(dir):
        return
    os.makedirs(os.path.dirname(dir), exist_ok=True)
    print(f"> cloning VTK {branch}")
    clone_cmd = f"git clone --depth 1 -b {branch} https://gitlab.kitware.com/vtk/vtk.git {dir}"
    print(f"> {clone_cmd}")
    subprocess.check_call(clone_cmd, shell=True)


def download_install_ninja_win(version="1.8.2", zip_file="src/ninja.zip"):
    os.makedirs(os.path.dirname(zip_file), exist_ok=True)
    if not os.path.isfile(zip_file):
        print(f"> downloading ninja v{version}")
        from urllib.request import urlretrieve
        url = f"https://github.com/ninja-build/ninja/releases/download/v{version}/ninja-win.zip"
        urlretrieve(url, zip_file)

    current = subprocess.check_output("ninja --version", shell=True).decode().strip()
    if version != current:
        print(f"> overwriting ninja (v{current}) with v{version}")
        scripts_dir = os.path.join(sys.prefix, "Scripts")
        import zipfile
        with zipfile.ZipFile(zip_file, 'r') as zh:
            zh.extractall(scripts_dir)

        current = subprocess.check_output("ninja --version", shell=True).decode().strip()
        if version != current:
            exit(f"> overwriting ninja FAILED")
        print(f"> overwriting ninja succeeded")


def download_install_cmake_win(major_version="3.10", version="3.10.2", zip_file="src/cmake.zip"):
    os.makedirs(os.path.dirname(zip_file), exist_ok=True)
    if not os.path.isfile(zip_file):
        print(f"> downloading cmake v{version}")
        from urllib.request import urlretrieve
        url = f"https://cmake.org/files/v{major_version}/cmake-{version}-win64-x64.zip"
        print(url)
        urlretrieve(url, zip_file)

        print(f"> overwriting cmake with v{version}")
        scripts_dir = os.path.join(sys.prefix, "Lib", "site-packages", "cmake", "data")
        import zipfile
        with zipfile.ZipFile(zip_file, 'r') as zh:
            zh.extractall(scripts_dir)

        print(f"> overwriting cmake succeeded")


def generate_libpython(filepath="work/vtk/libpython.notreally"):
    """
    According to PEP513 you are not allowed to link against libpythonxxx.so. However, CMake demands it. So here you go.
    An empty libpythonxxx.so.
    """
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, mode='w') as fh:
            fh.write('')
    return filepath


def build_vtk(src="../../src/vtk",
              python_library=None,
              python_include_dir=None,
              site_packages_dir=None,
              work="work/vtk",
              build="../../build_vtk",
              generator="Ninja",
              install_cmd="ninja install",
              install_dev=True,
              clean_cmake_cache=True):
    """Build and install VTK using CMake."""
    build_cmd = []
    if is_win:
        # only support VS2017 build tools for now
        vcvarsall_cmd = f"\"{setup_utils.get_vcvarsall()}\" amd64"
        build_cmd.append(vcvarsall_cmd)

    # compose cmake command
    cmake_cmd = ["cmake"]
    if clean_cmake_cache and os.path.exists(work):
        if is_win:
            cmake_cmd.append('"-U *"')
        else:
            cmake_cmd.append("-U *")
    cmake_cmd.extend([
        src,
        f"-G \"{generator}\"",
        "-DCMAKE_BUILD_TYPE=Release",
        # INSTALL options
        f"-DCMAKE_INSTALL_PREFIX:PATH={build}",
        f"-DVTK_INSTALL_PYTHON_MODULE_DIR:PATH=./{site_packages_dir}",
        f"-DVTK_INSTALL_LIBRARY_DIR:PATH=./{site_packages_dir}/vtk",  # install .so files into the python package
        f"-DVTK_INSTALL_ARCHIVE_DIR:PATH=./{site_packages_dir}/vtk",
        f"-DVTK_INSTALL_NO_DEVELOPMENT:BOOL={'ON' if not install_dev else 'OFF'}",
        # BUILD options
        "-DVTK_LEGACY_REMOVE:BOOL=ON",
        "-DBUILD_DOCUMENTATION:BOOL=OFF",
        "-DBUILD_TESTING:BOOL=OFF",
        "-DBUILD_EXAMPLES:BOOL=OFF",
        "-DBUILD_SHARED_LIBS:BOOL=ON",
        # PythonLibs options https://cmake.org/cmake/help/latest/module/FindPythonLibs.html
        f"-DPYTHON_INCLUDE_DIR:PATH=\"{python_include_dir}\"",
        f"-DPYTHON_LIBRARY:FILEPATH=\"{python_library}\"",
        # PythonInterp options https://cmake.org/cmake/help/latest/module/FindPythonInterp.html
        f"-DPYTHON_EXECUTABLE:FILEPATH=\"{sys.executable}\"",
        # Wrapping options
        "-DVTK_ENABLE_VTKPYTHON:BOOL=OFF",
        "-DVTK_WRAP_PYTHON:BOOL=ON",
        "-DVTK_WRAP_TCL:BOOL=OFF",
    ])
    # rpath settings
    # https://github.com/jcfr/VTKPythonPackage/blob/b30ce84696a3ea0bcf42052646a28bdf854ac819/CMakeLists.txt#L175
    # https://cmake.org/Wiki/CMake_RPATH_handling
    if is_darwin:
        cmake_cmd.extend([
            "-DCMAKE_INSTALL_NAME_DIR:STRING=@rpath",
            "-DCMAKE_INSTALL_RPATH:STRING=@loader_path",
            "-DCMAKE_OSX_DEPLOYMENT_TARGET='10.13'",
        ])
    elif not is_win:
        cmake_cmd.extend([
            "-DCMAKE_INSTALL_RPATH:STRING=\$ORIGIN",
        ])
    elif is_win:
        cmake_cmd.extend([
            "-DVTK_INSTALL_RUNTIME_DIR:PATH=./Scripts",
        ])

    build_cmd.append(" ".join(cmake_cmd))
    build_cmd.append(install_cmd)

    build_cmd = " && ".join(build_cmd)
    print(f"> configuring, building and installing VTK")
    print(f"> {build_cmd}")

    os.makedirs(work, exist_ok=True)
    subprocess.check_call(build_cmd, shell=True, cwd=work)


if __name__ == "__main__":
    if is_win:
        # windows requires the absolute latest of ninja and cmake to support VS2017 build tools
        download_install_ninja_win()
        download_install_cmake_win()

    clone_vtk()

    python_lib = setup_utils.get_python_lib()
    python_include_dir = setup_utils.get_python_include_dir()
    site_packages_dir = os.path.relpath(setup_utils.get_site_packages_dir(), sys.prefix)

    build_vtk(python_library=python_lib,
              python_include_dir=python_include_dir,
              site_packages_dir=site_packages_dir)

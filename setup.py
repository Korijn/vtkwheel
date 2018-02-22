import subprocess
import os
from setuptools import setup
import sys


is_win = (sys.platform == 'win32')
is_darwin = (sys.platform == 'darwin')


def clone_vtk(branch="v8.1.0", dir="src/vtk"):
    """Shallow-clone of VTK gitlab repo of tip of `branch` to `dir`."""
    if os.path.exists(dir):
        return
    print(f"> cloning VTK {branch}")
    clone_cmd = f"git clone --depth 1 -b {branch} https://gitlab.kitware.com/vtk/vtk.git {dir}"
    print(f"> {clone_cmd}")
    subprocess.check_call(f"git clone --depth 1 -b {branch} https://gitlab.kitware.com/vtk/vtk.git {dir}", shell=True)


def download_install_ninja_win(version="1.8.2", zip_file="src/ninja.zip"):
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


def build_vtk(src="../../src/vtk", work="work/vtk", build="../../build", generator="Ninja", install_cmd="ninja install"):
    """Build and install VTK using CMake."""
    build_cmd = []
    if is_win:
        python_include_dir = f"{sys.prefix}/include"
        python_library = f"{sys.prefix}/Scripts/python{sys.version_info[0]}{sys.version_info[1]}.dll"
        # only support VS2017 build tools for now
        vcvarsall_cmd = "\"C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools\\VC\\Auxiliary\\Build\\vcvarsall.bat\" amd64"
        build_cmd.append(vcvarsall_cmd)
        # could not get it to work with the version of ninja that is on pypi, so put it on the current path
        download_install_ninja_win()
    elif is_darwin:
        raise NotImplementedError("please define `python_library` for macOS")
    else:
        version_string = f"{sys.version_info[0]}.{sys.version_info[1]}{sys.abiflags}"
        python_include_dir = f"{sys.prefix}/include/python{version_string}"
        python_library = f"/usr/lib/x86_64-linux-gnu/libpython{version_string}.so"

    build_cmd.append(" ".join([
    f"cmake {src} -G \"{generator}\"",
        "-DCMAKE_BUILD_TYPE=Release",
        # INSTALL options
        f"-DCMAKE_INSTALL_PREFIX:PATH={build}",
        # BUILD options
        "-DBUILD_DOCUMENTATION:BOOL=OFF",
        "-DBUILD_TESTING:BOOL=OFF",
        "-DBUILD_EXAMPLES:BOOL=OFF",
        "-DBUILD_SHARED_LIBS:BOOL=ON",
        # PythonLibs options https://cmake.org/cmake/help/latest/module/FindPythonLibs.html
        f"-DPYTHON_INCLUDE_DIR:PATH=\"{python_include_dir}\"",
        f"-DPYTHON_LIBRARY:FILEPATH=\"{python_library}\"",
        # PythonInterp options https://cmake.org/cmake/help/latest/module/FindPythonInterp.html
        f"-DPYTHON_EXECUTABLE:FILEPATH=\"{sys.executable}\"",
        # VTK options
        "-DVTK_ENABLE_VTKPYTHON:BOOL=OFF",
        "-DVTK_WRAP_PYTHON:BOOL=ON",
    ]))
    os.makedirs(work, exist_ok=True)

    build_cmd.append(install_cmd)

    build_cmd = " && ".join(build_cmd)
    print(f"> configuring, building and installing VTK")
    print(f"> {build_cmd}")
    subprocess.check_call(build_cmd, shell=True, cwd=work)


# setup(

# )

if __name__ == "__main__":
    clone_vtk()
    build_vtk()

import subprocess
import os
from setuptools import setup
import sys


is_win = (sys.platform == 'win32')
is_darwin = (sys.platform == 'darwin')


def clone_vtk(branch="v8.1.0", dir="src/vtk"):
    """Shallow-clone of VTK gitlab repo of tip of `branch` to `dir`."""
    if os.path.exists(dir):
        print("> clone VTK destination already exists, skipping")
        return
    clone_cmd = f"git clone --depth 1 -b {branch} https://gitlab.kitware.com/vtk/vtk.git {dir}"
    print(f"> {clone_cmd}")
    subprocess.check_call(f"git clone --depth 1 -b {branch} https://gitlab.kitware.com/vtk/vtk.git {dir}", shell=True)


def build_vtk(src="../../src/vtk", work="work/vtk", build="../../build", generator="Ninja", install_cmd="ninja install"):
    """Build and install VTK using CMake."""
    build_cmd = []
    if is_win:
        python_library = f"{sys.prefix}/Scripts/python{sys.version_info[0]}{sys.version_info[1]}.dll"
        vcvarsall_cmd = "\"C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\BuildTools\\VC\\Auxiliary\\Build\\vcvarsall.bat\" amd64"
        build_cmd.append(vcvarsall_cmd)
        generator = "NMake Makefiles"
        install_cmd = "nmake install"
    
    if not os.path.isfile(python_library):
        raise ValueError("Could not find python_library. Please extend the code to detect it for your particular system/environment.")

    build_cmd.append(" ".join([
    f"cmake {src} -G \"{generator}\"",
        "-DCMAKE_BUILD_TYPE=Release",
        # install options
        f"-DCMAKE_INSTALL_PREFIX:PATH={build}",
        # build options
        "-DBUILD_DOCUMENTATION:BOOL=OFF",
        "-DBUILD_TESTING:BOOL=OFF",
        "-DBUILD_EXAMPLES:BOOL=OFF",
        "-DBUILD_SHARED_LIBS:BOOL=ON",
        # python options
        #"-DVTK_PYTHON_VERSION:STRING=3.6",
        f"-DPYTHON_EXECUTABLE:FILEPATH=\"{sys.executable}\"",
        f"-DPYTHON_INCLUDE_DIR:PATH=\"{sys.prefix}/include\"",
        f"-DPYTHON_LIBRARY:FILEPATH=\"{python_library}\"",
        # wrapping options
        "-DVTK_ENABLE_VTKPYTHON:BOOL=OFF",
        "-DVTK_WRAP_PYTHON:BOOL=ON",
    ]))
    os.makedirs(work, exist_ok=True)

    build_cmd.append(install_cmd)

    build_cmd = " && ".join(build_cmd)
    print(f"> {build_cmd}")
    subprocess.check_call(build_cmd, shell=True, cwd=work)


# setup(

# )

if __name__ == "__main__":
    clone_vtk()
    build_vtk()

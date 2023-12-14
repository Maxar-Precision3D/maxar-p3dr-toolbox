# Integration Toolbox - Maxar Precision 3D Registration (P3DR)

This repository contains a set of Python packages helpful for an integrator of Maxar Precision 3D Registration (P3DR).

The Python packages all have limited and basic functionality.

## Toolbox Packages

The Python packages in the toolbox are:

| Package/directory                              | Description                              |
|------------------------------------------------|------------------------------------------|
| [maxar_canv](maxar_canv/README.md)             | Maxar Canonical Video format (canv)      |
| [maxar_p3dr_video](maxar_p3dr_video/README.md) | Video Registration using P3DR Server     |
| [maxar_tiny_geo](maxar_tiny_geo/README.md)     | Utility for simple geoconversions        |
| [maxar_tiny_cam](maxar_tiny_cam/README.md)     | Utility for common camera transforms     |
| [maxar_tiny_fit](maxar_tiny_fit/README.md)     | Minimal Gauss-Newton solver              |
| [maxar_tiny_rpc](maxar_tiny_rpc/README.md)     | Minimal utility for RPC                  |

## Local Installation

To build and install the toolbox packages in a virtual environment, start by creating and activating the virtual
environment, and then install the Python build utility. The following instructions expects the current working directory to
be located in the root of the repository.

**Note:** See instruction on downloading [external resources for maxar_tiny_geo](maxar_tiny_geo/src/maxar_tiny_geo/resources/README.md)

```console
$ python -m venv env
$ source env/bin/activate
$ python -m pip install --upgrade pip
$ python -m pip install --upgrade build
```

Then continue with the package build and local installation in the following order. Note that the package versions
used for the install command reflects the current versions.

```console
$ python -m build maxar_canv
$ python -m pip install maxar_canv/dist/maxar_canv-0.0.3-py3-none-any.whl
```

```console
$ python -m build maxar_p3dr_video
$ python -m pip install maxar_p3dr_video/dist/maxar_p3dr_video-0.0.3-py3-none-any.whl
```

```console
$ python -m build maxar_tiny_geo
$ python -m pip install maxar_tiny_geo/dist/maxar_tiny_geo-0.0.4-py3-none-any.whl
```

```console
$ python -m build maxar_tiny_cam
$ python -m pip install maxar_tiny_cam/dist/maxar_tiny_cam-0.0.2-py3-none-any.whl
```

```console
$ python -m build maxar_tiny_fit
$ python -m pip install maxar_tiny_fit/dist/maxar_tiny_fit-0.0.2-py3-none-any.whl
```

```console
$ python -m build maxar_tiny_rpc
$ python -m pip install maxar_tiny_rpc/dist/maxar_tiny_rpc-0.0.2-py3-none-any.whl
```

If successful a listing of the content in the virtual environment should look like.

```console
$ python -m pip list
Package            Version
------------------ ----------
build              1.0.3
certifi            2023.11.17
importlib-metadata 6.8.0
maxar-canv         0.0.3
maxar-p3dr-video   0.0.3
maxar-tiny-cam     0.0.2
maxar-tiny-fit     0.0.2
maxar-tiny-geo     0.0.4
maxar-tiny-rpc     0.0.2
numpy              1.24.4
packaging          23.2
parsy              2.1
Pillow             9.5.0
pip                23.3.1
protobuf           3.18.0
pyproj             3.5.0
pyproject_hooks    1.0.0
pyquaternion       0.9.9
setuptools         41.6.0
tomli              2.0.1
zipp               3.17.0
```

## Requirements

The Python packages in the toolbox all requires Python version 3.8 or later. Linux is the recommended execution envorinment.
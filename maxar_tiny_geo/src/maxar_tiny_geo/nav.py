"""
Module with functionality related to rotations in a navigation frame.
"""
from __future__ import annotations  # noqa

import math
import numpy as np
from numpy.typing import ArrayLike, NDArray


def local_ned_axes(llh: ArrayLike) -> NDArray:
    """
    Create a local NED frame given the geodetic location.

    Parameters:
        llh: Array with latitude (degrees), longitude (degrees), height.

    Returns:
        3x3 rotation matrix with basis vectors for north, east and down.
    """
    assert len(llh) == 3

    lat, lon, _ = np.radians(llh)

    slat = math.sin(lat)
    clat = math.cos(lat)
    slon = math.sin(lon)
    clon = math.cos(lon)

    mat = np.empty((3, 3), dtype=np.float64)
    mat[0, 0] = -slat * clon
    mat[0, 1] = -slon
    mat[0, 2] = -clat * clon

    mat[1, 0] = -slat * slon
    mat[1, 1] = clon
    mat[1, 2] = -clat * slon

    mat[2, 0] = clat
    mat[2, 1] = 0.
    mat[2, 2] = -slat

    return mat


def euler_zyx(ypr: ArrayLike) -> NDArray:
    """
    Create an Euler rotation matrix for the axis order z, y, x.

    Parameters:
      ypr: Array with yaw, pitch and roll in radians.

    Returns:
      3x3 rotation matrix.
    """

    assert len(ypr) == 3

    z, y, x = ypr

    cz = math.cos(z)
    sz = math.sin(z)
    cy = math.cos(y)
    sy = math.sin(y)
    cx = math.cos(x)
    sx = math.sin(x)

    mat = np.empty((3, 3), dtype=np.float64)
    mat[0, 0] = cy * cz
    mat[0, 1] = cz * sx * sy - cx * sz
    mat[0, 2] = cx * cz * sy + sx * sz

    mat[1, 0] = cy * sz
    mat[1, 1] = cx * cz + sx * sy * sz
    mat[1, 2] = -cz * sx + cx * sy * sz

    mat[2, 0] = -sy
    mat[2, 1] = cy * sx
    mat[2, 2] = cx * cy

    return mat


def eulerd_zyx(ypr: ArrayLike) -> NDArray:
    """
    Create an Euler rotation matrix for the axis order z, y, x.

    Parameters:
        ypr: Array with yaw, pitch and roll in degrees.

    Returns:
        3x3 rotation matrix.
    """
    return euler_zyx(np.radians(ypr))


def decomp_euler_zyx(mat: NDArray) -> NDArray:
    """
    Decompose a rotation matrix into Euler angles, given the
    axis order z, y, x.

    Parameters:
        mat: 3x3 rotation matrix.

    Returns:
        Array with Euler angles yaw, pitch and roll in radians.
    """
    assert mat.shape == (3, 3)

    y = math.atan2(mat[1, 0], mat[0, 0])
    p = math.asin(-mat[2, 0])
    r = math.atan2(mat[2, 1], mat[2, 2])

    return np.array((y, p, r))


def decomp_eulerd_zyx(mat: NDArray) -> NDArray:
    """
    Decompose a rotation matrix into Euler angles, given the
    axis order z, y, x.

    Parameters:
        mat: 3x3 rotation matrix.

    Returns:
        Array with Euler angles yaw, pitch and roll in degrees.
    """
    return np.degrees(decomp_euler_zyx(mat))

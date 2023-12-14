"""
Module with coordinate transformations between WGS84 geodetic coordinates
using ELLIPSOID or EGM2008 height and ECEF coordinates.

Correspondence to Eufori implementation:
egm2008   -> "ITRF2008[2005.0]:GEOD[NED:D],EGM2008"
ellipsoid -> "ITRF2008[2005.0]:GEOD[NED:D],ELLIPSOID"
ecef      -> "ITRF2008[2005.0]:GEOC"

Note: A difference compared to Eufori is that maxar_tiny_geo don't use
negative heights for EGM2008 and ELLIPSOID coordinates.
"""

from __future__ import annotations  # noqa

from .nav import local_ned_axes, eulerd_zyx, decomp_eulerd_zyx

import numpy as np
from numpy.typing import ArrayLike, NDArray
import pathlib
import pyproj

__egm2008_to_ecef = None
__ecef_to_egm2008 = None
__ellipsoid_to_ecef = None
__ecef_to_ellipsoid = None


def setup() -> bool:
    """
    Setup the geo transformers. Required for coordinate transformations.
    Automatically called by package init, and a RuntimeError is raised
    if the setup is failing.

    Returns:
        True if the setup was successful, otherwise False.
    """
    global __egm2008_to_ecef
    global __ecef_to_egm2008
    global __ellipsoid_to_ecef
    global __ecef_to_ellipsoid

    if __egm2008_to_ecef is not None and __ecef_to_egm2008 is not None \
            and __ellipsoid_to_ecef is not None and __ecef_to_ellipsoid is not None:
        print('Already setup')
        return True

    geoid_path = pathlib.Path(__file__).parent / 'resources' / 'egm08_25.gtx'

    if geoid_path.exists() and geoid_path.is_file():
        egm2008_str = f'+proj=latlon +use_geoid +datum=WGS84 +geoidgrids={str(geoid_path)}'
        ellipsoid_str = '+proj=latlon +use_ellipsoid +datum=WGS84'
        ecef_str = '+proj=geocent +datum=WGS84'

        egm2008 = pyproj.CRS.from_proj4(egm2008_str)
        ellipsoid = pyproj.CRS.from_proj4(ellipsoid_str)
        ecef = pyproj.CRS.from_proj4(ecef_str)

        __egm2008_to_ecef = pyproj.Transformer.from_crs(egm2008, ecef)
        __ecef_to_egm2008 = pyproj.Transformer.from_crs(ecef, egm2008)

        __ellipsoid_to_ecef = pyproj.Transformer.from_crs(ellipsoid, ecef)
        __ecef_to_ellipsoid = pyproj.Transformer.from_crs(ecef, ellipsoid)

        return True
    else:
        print(f'Failed to find geoid. Tried={geoid_path}')
        return False


def egm2008_to_ecef(pose: ArrayLike) -> NDArray:
    """
    Transform from a geodetic EGM2008 location or pose to a
    geocentric ECEF location or pose.

    All angles are supposed to be in degrees.

    Parameters:
        pose: Array with latitude, longitude, height or
              array with latitude, longitude, height, yaw, pitch, roll

    Returns:
        Array with x, y, z or, array with x, y, z, yaw, pitch, roll
    """
    assert __egm2008_to_ecef is not None
    return __to_ecef(pose, __egm2008_to_ecef)


def ellipsoid_to_ecef(pose: ArrayLike) -> NDArray:
    """
    Transform from a geodetic ELLIPSOID location or pose to a
    geocentric ECEF location or pose.

    All angles are supposed to be in degrees.

    Parameters:
        pose: Array with latitude, longitude, height or
              array with latitude, longitude, height, yaw, pitch, roll

    Returns:
        Array with x, y, z or, array with x, y, z, yaw, pitch, roll
    """
    assert __ellipsoid_to_ecef is not None
    return __to_ecef(pose, __ellipsoid_to_ecef)


def ecef_to_egm2008(pose: ArrayLike) -> NDArray:
    """
    Transform from a geocentric ECEF location or pose to a geodetic EGM2008 
    location or pose.

    All angles are supposed to be in degrees.

    Parameters:
        pose: Array with x, y and z or
              array with x, y, z, yaw, pitch, roll    

    Returns:
        Array with latitude, longitude and height or
        array with latitude, longitude, height, yaw, pitch, roll
    """
    assert __ecef_to_egm2008 is not None
    return __from_ecef(pose, __ecef_to_egm2008)


def ecef_to_ellipsoid(pose: ArrayLike) -> NDArray:
    """
    Transform from a geocentric ECEF location or pose to a geodetic ELLIPSOID 
    location or pose.

    All angles are supposed to be in degrees.

    Parameters:
        pose: Array with x, y and z or
              array with x, y, z, yaw, pitch, roll    

    Returns:
        Array with latitude, longitude and height or
        array with latitude, longitude, height, yaw, pitch, roll
    """
    assert __ecef_to_ellipsoid is not None
    return __from_ecef(pose, __ecef_to_ellipsoid)


def __to_ecef(pose: ArrayLike, T: pyproj.Transformer) -> NDArray:
    if len(pose) == 3:
        lat, lon, h = pose
        return np.array(T.transform(lon, lat, h))
    elif len(pose) == 6:
        llh = pose[:3]
        ypr = pose[3:]

        mat = local_ned_axes(llh) @ eulerd_zyx(ypr)
        eulerd = decomp_eulerd_zyx(mat)

        lat, lon, h = llh
        return np.append(T.transform(lon, lat, h), eulerd)
    else:
        raise ValueError('Pose array must have either three or six elements')


def __from_ecef(pose: ArrayLike, T: pyproj.Transformer) -> NDArray:
    if len(pose) == 3:
        x, y, z = pose
        lon, lat, h = T.transform(x, y, z)
        return np.array((lat, lon, h))
    elif len(pose) == 6:
        x, y, z = pose[:3]
        ypr = pose[3:]

        lon, lat, h = T.transform(x, y, z)
        llh = lat, lon, h

        mat = local_ned_axes(llh).T @ eulerd_zyx(ypr)
        eulerd = decomp_eulerd_zyx(mat)

        return np.append(llh, eulerd)
    else:
        raise ValueError('Pose array must have either three or six elements')

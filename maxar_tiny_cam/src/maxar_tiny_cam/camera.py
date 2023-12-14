from __future__ import annotations  # noqa

from .lens import Lens

import maxar_tiny_geo as geo

import math
import numpy as np
from numpy.typing import ArrayLike, NDArray
from pyquaternion import Quaternion
from typing import Any, Dict


class Camera:
    """
    Pinhole camera class, intended to work within the ECEF frame of
    reference. The camera can be directly created with a
    quaternion, describing the global yaw (Z), pitch (Y) and roll (X)
    attitudes, the ECEF position and a Lens object.

    The camera can also be initialized through several helper
    functions.
    """

    def __init__(self: Camera,
                 attitude: Quaternion,
                 position: ArrayLike,
                 lens: Lens) -> None:
        """
        Create a Camera object.

        Parameters:
            attitude: The global ECEF attitude expressed as a quaternion.
            position: The ECEF position for the camera.
            lens: The Lens object for the camera.
            k2, k3, k4: Coefficients for radial distortion.

        """
        self._poseQ = attitude
        self._viewQ = attitude.conjugate
        self._position = np.array(position)

        permute = Quaternion(axis=(0.0, 0.0, 1.0), degrees=-90) * \
            Quaternion(axis=(0.0, 1.0, 0.0), degrees=-90)

        self._lensQ = permute
        self._nedQ = permute.conjugate

        self._lens = lens

    @staticmethod
    def from_canonic(canonic: Dict[str, Any]) -> Camera | None:
        """
        Create a Camera from a Canonic camera description.

        Parameters:
            canonic: A Canonic camera dictionary.

        Returns:
            A Camera object, or None if failed to read dictionary.
        """
        try:
            llh = canonic['pos']
            llh[2] *= -1.0

            ypr = np.degrees(canonic['att'])

            lens = canonic['lens']
            hfov = math.degrees(lens['hfov'])
            vfov = math.degrees(lens['vfov'])
            k2 = lens.get('k2', 0.0)
            k3 = lens.get('k3', 0.0)
            k4 = lens.get('k4', 0.0)

            return Camera.from_euler_egm2008(llh=llh, ypr=ypr, fov=(hfov, vfov),
                                             k2=k2, k3=k3, k4=k4)
        except KeyError as e:
            print(f'Missing key={e}')
            return None

    @staticmethod
    def from_euler_ellipsoid(llh: ArrayLike,
                             ypr: ArrayLike,
                             fov: tuple[float, float],
                             k2: float = 0.,
                             k3: float = 0.,
                             k4: float = 0.) -> Camera:
        """
        Create a Camera from latitude, longitude, height above the ellipsoid 
        and geodetic attitude.

        Parameters:
            llh: Array with latitude, longitude and height.
            ypr: Array with yaw, pitch and roll (in degrees).
            fov: Tuple with field of view (horizontal, vertical) in degrees.
            k2, k3, k4: Coefficients for radial distortion.

        Returns:
            A Camera object.
        """
        ecef = geo.ellipsoid_to_ecef(np.append(llh, ypr))
        return Camera.from_euler_ecef(xyz=ecef[:3], ypr=ecef[3:],
                                      fov=fov, k2=k2, k3=k3, k4=k4)

    @staticmethod
    def from_euler_egm2008(llh: ArrayLike,
                           ypr: ArrayLike,
                           fov: tuple[float, float],
                           k2: float = 0.,
                           k3: float = 0.,
                           k4: float = 0.) -> Camera:
        """
        Create a Camera from latitude, longitude, height above the EGM2008 geoid 
        and geodetic attitude.

        Parameters:
            llh: Array with latitude, longitude and height.
            ypr: Array with yaw, pitch and roll (in degrees).
            fov: Tuple with field of view (horizontal, vertical) in degrees.
            k2, k3, k4: Coefficients for radial distortion.

        Returns:
            A Camera object.
        """
        ecef = geo.egm2008_to_ecef(np.append(llh, ypr))
        return Camera.from_euler_ecef(xyz=ecef[:3], ypr=ecef[3:],
                                      fov=fov, k2=k2, k3=k3, k4=k4)

    @staticmethod
    def from_euler_ecef(xyz: ArrayLike,
                        ypr: ArrayLike,
                        fov: tuple[float, float],
                        k2: float = 0.,
                        k3: float = 0.,
                        k4: float = 0.) -> Camera:
        """
        Create a Camera from ECEF coordinates and geocentric
        attitude.

        Parameters:
            xyz: Array with x, y and z.
            ypr: Array with global yaw, pitch and roll (in degrees).
            fov: Tuple with field of view (horizontal, vertical) in degrees.
            k2, k3, k4: Coefficients for radial distortion.

        Returns:
            A Camera object.
        """
        return Camera.from_R_t(R=geo.eulerd_zyx(ypr), t=xyz, fov=fov,
                               k2=k2, k3=k3, k4=k4)

    @staticmethod
    def from_R_t(R: NDArray,
                 t: ArrayLike,
                 fov: tuple[float, float],
                 k2: float = 0.,
                 k3: float = 0.,
                 k4: float = 0.) -> Camera:
        """
        Create a Camera from a global, ECEF, 3x3 rotations matrix and a 
        geocentric position.

        Parameters:
            R: 3x3 rotation matrix.
            t: Array with x, y and z to give the translation (position).
            k2, k3, k4: Coefficients for radial distortion.

        Returns:
            A Camera object.
        """
        attitude = Quaternion(matrix=R)
        lens = Lens(fov=fov, k2=k2, k3=k3, k4=k4)
        return Camera(attitude=attitude, position=t, lens=lens)

    def ellipsoid_to_uv(self: Camera, llh: ArrayLike) -> NDArray:
        """
        Project a geodetic coordinate to an uv coordinate on the image plane.

        Parameters:
           llh: Array with latitude, longitude and height (above the ellipsoid). 

        Returns:
            Uv coordinate, where the "visible" area is in range 0, 0 to 1, 1.
        """
        return self.xyz_to_uv(geo.ellipsoid_to_ecef(llh))

    def egm2008_to_uv(self: Camera, llh: ArrayLike) -> NDArray:
        """
        Project a geodetic coordinate to an uv coordinate on the image plane.

        Parameters:
           llh: Array with latitude, longitude and height (above the EGM2008 geoid). 

        Returns:
            Uv coordinate, where the "visible" area is in range 0, 0 to 1, 1.
        """
        return self.xyz_to_uv(geo.egm2008_to_ecef(llh))

    def xyz_to_uv(self: Camera, xyz: ArrayLike) -> NDArray:
        """
        Project an ECEF coordinate to an uv coordinate on the image plane.

        Parameters:
            xyz: ECEF coordinate.

        Returns:
            Uv coordinate, where the "visible" area is in range 0, 0 to 1, 1.
        """
        uv, _ = self.xyz_to_uv_depth(xyz)
        return uv

    def xyz_to_uv_depth(self: Camera, xyz: ArrayLike) -> tuple[NDArray, float]:
        """
        Project an ECEF coordinate to an uv coordinate on the image plane.

        Parameters:
            xyz: ECEF coordinate.

        Returns:
            Tuple with uv coordinate and the camera relative depth for the
            coordinate.
        """
        xyz = np.array(xyz)
        xyz -= self._position

        xyz = Quaternion.rotate(self._viewQ, xyz)
        xyz = Quaternion.rotate(self._lensQ, xyz)

        return self._lens.xyz_to_uv(xyz), xyz[2]

    def uv_to_xyz(self: Camera, uv: ArrayLike, depth: float = 1.0) -> NDArray:
        """
        Reconstruct an ECEF coordinate from uv. To get an exact reconstruction
        a depth value is needed.

        Parameters:
            uv: Uv coordinate.
            depth: The depth of the coordinate into the scene (default 1.0).

        Returns:
            The reconstructed ECEF coordinate. The default depth of the coordinate
            is 1.0 (i.e. one meter from the camera along the principal axis).
        """
        xyz = self._lens.uv_to_xyz(uv) * depth

        xyz = Quaternion.rotate(self._nedQ, xyz)
        xyz = Quaternion.rotate(self._poseQ, xyz)

        return xyz + self._position

    def uv_to_ray(self: Camera, uv: ArrayLike) -> tuple[NDArray, NDArray]:
        """
        Get a unit length ray for the uv.

        Parameters:
            uv: Uv coordinate.

        Returns tuple with ray origin and ray direction.
        """
        xyz = self.uv_to_xyz(uv)

        dir = xyz - self._position
        dir /= np.linalg.norm(dir)

        return self._position, dir

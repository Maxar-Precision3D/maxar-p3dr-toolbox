from __future__ import annotations  # noqa

import numpy as np
from numpy.typing import ArrayLike, NDArray


class Lens:
    """
    A simple lens model extending the pinhole model with radial lens
    distortion using the coefficients k2, k3 and k4.
    """

    def __init__(self: Lens, fov: tuple[float, float],
                 k2: float = 0., k3: float = 0., k4: float = 0.) -> None:
        """
        Construct a Lens object.

        Parameters:
            fov: Tuple (horizontal, vertical) field of view in degrees.
            k2: Radial distortion coefficient.
            k3: Radial distortion coefficient.
            k4: Radial distortion coefficient.
        """
        assert len(fov) == 2

        # Coefficients for radial distortion.
        self._k2 = k2
        self._k3 = k3
        self._k4 = k4

        # Focal length (default set to one).
        self._f = 1.0

        # Inverse f.
        self._inv_f = 1.0 / self._f

        # Effective sensor size (function of focal length and fov).
        self._size = np.tan(np.radians(fov) / 2.) * 2. * self._f

    def xyz_to_uv(self: Lens, xyz: ArrayLike) -> NDArray:
        """
        Project a camera frame xyz coordinate to the lens.

        Parameters:
            xyz: The coordinate (z must be > zero).

        Returns:
            Uv coordinate, where the "visible" area is in range 0, 0 to 1, 1.
        """
        assert len(xyz) == 3
        assert xyz[2] > 0.

        # Normalize to a depth of 1.0.
        xyz = np.array(xyz)
        xyz /= xyz[2]

        xy = xyz[:2]
        z = xyz[2]

        # Scale xy by radial distortion.
        s = self.radial_distortion(np.linalg.norm(xy))
        xy *= s

        uv = self._f * xy / z
        uv /= self._size

        return uv + 0.5

    def uv_to_xyz(self: Lens, uv: ArrayLike) -> NDArray:
        """
        Reconstruct a camera frame xyz coordinate from the uv coordinate.
        The reconstructed coordinate always has the depth of 1.

        Parameters:
            uv: Uv coordinate.

        Returns:
            Xyz coordinate in the camera frame.
        """
        assert len(uv) == 2

        uv = np.array(uv) - 0.5
        uv *= self._size
        xy = uv * self._inv_f

        # Scale xy by inverse radial distortion.
        s = self.inv_radial_distortion(np.linalg.norm(xy))
        xy *= s

        return np.append(xy, 1.)

    def radial_distortion(self: Lens, r: float) -> float:
        r2 = r * r
        r3 = r2 * r
        r4 = r2 * r2

        return 1. + self._k2 * r2 + self._k3 * r3 + self._k4 * r4

    def inv_radial_distortion(self: Lens, r: float) -> float:
        r2 = r * r
        r3 = r * r2
        r4 = r2 * r2

        k2a = self._k2 * r2
        k2b = k2a * 3.

        k3a = self._k3 * r3
        k3b = k3a * 4.

        k4a = self._k4 * r4
        k4b = k4a * 5.

        f0 = k2a + k3a + k4a
        f1 = 1. + k2b + k3b + k4b

        c = 1.
        c -= f0 / f1

        for _ in range(5):
            c2 = c * c
            c3 = c2 * c
            c4 = c2 * c2
            c5 = c2 * c3

            f0 = c + c3 * k2a + c4 * k3a + c5 * k4a - 1.
            f1 = 1. + c2 * k2b + c3 * k3b + c4 * k4b
            c -= f0 / f1

        return c

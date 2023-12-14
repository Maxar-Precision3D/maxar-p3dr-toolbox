"""
The rpc module provides the Rpc class, which is encapsulating
basic RPC functionality like reading from file, and perform
operations ground_to_image and image_to_ground.
"""
from __future__ import annotations  # noqa

from .reader import read_file

import numpy as np
from numpy.typing import ArrayLike, NDArray
from maxar_tiny_fit import leastsq
import pathlib


class Rpc:
    """
    Rpc class. Shall be constructed using from_file rather than using
    the constructor.
    """

    def __init__(self: Rpc) -> None:
        """
        Initialization of an Rpc object. Default everything is initialized
        to None and the object is invalid. Use Rpc.from_file to initialize
        an object from file contents.
        """
        self._image_off = None
        self._image_scale = None
        self._geo_off = None
        self._geo_scale = None
        self._line_num_coeff = None
        self._line_den_coeff = None
        self._samp_num_coeff = None
        self._samp_den_coeff = None

    @staticmethod
    def from_file(path: pathlib.Path) -> Rpc | None:
        """
        Create an Rpc object from a file (either .RPB, .rpc or _rpc.txt).

        Parameters:
            path: A path to the RPC-file.

        Returns:
            An Rpc object, or None if fail.
        """
        data = read_file(path)
        if data is None:
            return None

        self = Rpc()

        self._image_off = data['IMAGE_OFF']
        self._image_scale = data['IMAGE_SCALE']
        self._geo_off = data['GEO_OFF']
        self._geo_scale = data['GEO_SCALE']

        self._line_num_coeff = data['LINE_NUM_COEFF']
        self._line_den_coeff = data['LINE_DEN_COEFF']
        self._samp_num_coeff = data['SAMP_NUM_COEFF']
        self._samp_den_coeff = data['SAMP_DEN_COEFF']

        return self

    def valid(self: Rpc) -> bool:
        """
        Check if the Rpc object is valid for use.

        Returns:
            True if the object is valid, else False.
        """
        return self._image_off is not None and \
            self._image_scale is not None and \
            self._geo_off is not None and \
            self._geo_scale is not None and \
            self._line_num_coeff is not None and \
            self._line_den_coeff is not None and \
            self._samp_num_coeff is not None and \
            self._samp_den_coeff is not None

    def ground_to_image(self: Rpc, llh: ArrayLike) -> NDArray:
        """
        Project a ground point to the image plane.

        Parameters:
            llh: An array-like sequence of latitude, longitude and height.

        Returns:
            A numpy array with x (sample) and y (line) in pixel coordinates.
        """
        assert self.valid()

        P, L, H = (np.array(llh) - self._geo_off) / self._geo_scale
        p = Rpc._geo_array(P, L, H)
        c = np.dot(self._samp_num_coeff, p) / np.dot(self._samp_den_coeff, p)
        r = np.dot(self._line_num_coeff, p) / np.dot(self._line_den_coeff, p)

        return (np.array((c, r)) * self._image_scale) + self._image_off

    def image_to_ground(self: Rpc, px: ArrayLike, height: float) -> NDArray | None:
        """
        For a given height find the latitude and longitude for an image pixel.

        Parameters:
            px: Array-like sequence of x (sample) and y (line) pixel coordinates.

        Returns:
            A numpy array with latitude, longitude and height. Or None if fail.
        """
        assert self.valid()

        # The initial guess is the lat, long at the center of the RPC.
        x0 = self._geo_off[:2].copy()

        # Function to evaluate reprojection error during fitting.
        def func(x: NDArray) -> NDArray:
            x = np.append(x, height)

            px_hat = self.ground_to_image(x)

            # Trick: to have as many residuals as parameters don't take
            # the norm of the difference, instead let each pixel coordinate
            # become its own residual.
            return px_hat - px

        result = leastsq(func, x0, steps=1e-08)
        if result['successful']:
            return np.append(result['params'], height)
        else:
            print(f"Error: {result['message']}")
            return None

    @staticmethod
    def _geo_array(P: float, L: float, H: float) -> NDArray:
        arr = np.empty(20, dtype=np.float64)
        arr[0] = 1.
        arr[1] = L
        arr[2] = P
        arr[3] = H
        arr[4] = L * P
        arr[5] = L * H
        arr[6] = P * H
        arr[7] = L ** 2
        arr[8] = P ** 2
        arr[9] = H ** 2
        arr[10] = P * L * H
        arr[11] = L ** 3
        arr[12] = L * P ** 2
        arr[13] = L * H ** 2
        arr[14] = L ** 2 * P
        arr[15] = P ** 3
        arr[16] = P * H ** 2
        arr[17] = L ** 2 * H
        arr[18] = P ** 2 * H
        arr[19] = H ** 3

        return arr

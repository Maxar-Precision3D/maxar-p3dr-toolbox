"""
The maxar_tiny_geo package provides basic coordinate transformations.
"""
from .nav import local_ned_axes, euler_zyx, decomp_euler_zyx, eulerd_zyx, decomp_eulerd_zyx  # noqa
from .transform import setup, egm2008_to_ecef, ecef_to_egm2008, ellipsoid_to_ecef, ecef_to_ellipsoid  # noqa

if not setup():
    raise RuntimeError('Failed to setup maxar_tiny_geo')

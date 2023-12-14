# Maxar Tiny Geo

This Python package provides an integrator with a programmatic interface as well as a CLI for common geoconversions:

```console
python -m maxar_tiny_geo -h
usage: python -m maxar_tiny_geo [-h] [--egm2008-to-ecef] [--ellipsoid-to-ecef]
                                [--ecef-to-egm2008] [--ecef-to-ellipsoid]
                                GEOTERM [GEOTERM ...]

positional arguments:
  GEOTERM              Position or attitude term (three or six terms in total)

optional arguments:
  -h, --help           show this help message and exit
  --egm2008-to-ecef    Convert from EGM2008 to ECEF
  --ellipsoid-to-ecef  Convert from ELLIPSOID to ECEF
  --ecef-to-egm2008    Convert from ECEF to EGM2008
  --ecef-to-ellipsoid  Convert from ECEF to ELLIPSOID
  ```

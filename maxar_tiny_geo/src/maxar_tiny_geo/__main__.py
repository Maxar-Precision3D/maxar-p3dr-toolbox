from maxar_tiny_geo import egm2008_to_ecef, ellipsoid_to_ecef, ecef_to_egm2008, ecef_to_ellipsoid

import argparse
import numpy as np
import sys


def main() -> bool:
    parser = argparse.ArgumentParser('python -m maxar_tiny_geo')
    parser.add_argument('geoterms', metavar='GEOTERM',
                        type=float, nargs='+',
                        help="Position or attitude term (three or six terms in total)")
    parser.add_argument('--egm2008-to-ecef', action='store_true',
                        help='Convert from EGM2008 to ECEF')
    parser.add_argument('--ellipsoid-to-ecef', action='store_true',
                        help='Convert from ELLIPSOID to ECEF')
    parser.add_argument('--ecef-to-egm2008', action='store_true',
                        help='Convert from ECEF to EGM2008')
    parser.add_argument('--ecef-to-ellipsoid', action='store_true',
                        help='Convert from ECEF to ELLIPSOID')
    opts = parser.parse_args()

    if len(opts.geoterms) != 3 and len(opts.geoterms) != 6:
        print('The number of GEOTERMS must either be three or six\n')
        parser.print_usage()
        return False

    if opts.egm2008_to_ecef:
        print(egm2008_to_ecef(opts.geoterms))
    elif opts.ellipsoid_to_ecef:
        print(ellipsoid_to_ecef(opts.geoterms))
    elif opts.ecef_to_egm2008:
        print(ecef_to_egm2008(opts.geoterms))
    elif opts.ecef_to_ellipsoid:
        print(ecef_to_ellipsoid(opts.geoterms))
    else:
        print('A conversion mode must be set\n')
        parser.print_usage()
        return False

    return True


if __name__ == '__main__':
    np.set_printoptions(suppress=True)
    sys.exit(0 if main() else 1)

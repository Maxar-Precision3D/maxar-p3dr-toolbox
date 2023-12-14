from __future__ import annotations  # noqa

import maxar_tiny_rpc.reader.rpb as rpb

import unittest


class RpbTest(unittest.TestCase):
    """
    Testing a few RPC specific things.
    """

    def test_numeric_assignment(self: RpbTest) -> None:
        str = 'errBias = 5.91;'

        key, val = rpb.assignment().parse(str)
        self.assertEqual('errBias', key)
        self.assertEqual(5.91, val)

    def test_string_assignment(self: RpbTest) -> None:
        str = 'satId = "WV02";'

        key, val = rpb.assignment().parse(str)
        self.assertEqual('satId', key)
        self.assertEqual('WV02', val)

    def test_array_assignment(self: RpbTest) -> None:
        str = """lineNumCoef = (
                        +7.428028E-03,
                        -8.063566E-03,
                        -1.045865E+00,
                        +3.703674E-02,
                        +1.613177E-03,
                        -5.751060E-05,
                        +1.580106E-04,
                        -2.322813E-03,
                        -4.323626E-03,
                        -3.170007E-06,
                        -4.700669E-07,
                        +3.595122E-06,
                        +8.111353E-06,
                        +1.807670E-08,
                        -1.090181E-05,
                        -1.483183E-05,
                        +8.607110E-07,
                        +2.691113E-07,
                        +7.095370E-07,
                        -3.406377E-08);
        """

        key, val = rpb.assignment().parse(str)
        self.assertEqual('lineNumCoef', key)
        self.assertIsInstance(val, list)
        self.assertEqual(20, len(val))

        self.assertEqual(+7.428028E-03, val[0])
        self.assertEqual(-8.063566E-03, val[1])
        self.assertEqual(-1.045865E+00, val[2])
        self.assertEqual(+3.703674E-02, val[3])
        self.assertEqual(+1.613177E-03, val[4])
        self.assertEqual(-5.751060E-05, val[5])
        self.assertEqual(+1.580106E-04, val[6])
        self.assertEqual(-2.322813E-03, val[7])
        self.assertEqual(-4.323626E-03, val[8])
        self.assertEqual(-3.170007E-06, val[9])
        self.assertEqual(-4.700669E-07, val[10])
        self.assertEqual(+3.595122E-06, val[11])
        self.assertEqual(+8.111353E-06, val[12])
        self.assertEqual(+1.807670E-08, val[13])
        self.assertEqual(-1.090181E-05, val[14])
        self.assertEqual(-1.483183E-05, val[15])
        self.assertEqual(+8.607110E-07, val[16])
        self.assertEqual(+2.691113E-07, val[17])
        self.assertEqual(+7.095370E-07, val[18])
        self.assertEqual(-3.406377E-08, val[19])

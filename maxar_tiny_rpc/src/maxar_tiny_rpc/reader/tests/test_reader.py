from __future__ import annotations # noqa


from maxar_tiny_rpc.reader import read_file

import numpy as np
import pathlib
import unittest


class ReaderTest(unittest.TestCase):
    """
    Smoke tests for RPC parsing.
    """

    def test_correct_files(self: ReaderTest) -> None:
        data_dir = pathlib.Path(__file__).parent.absolute() / 'data'

        # Read the files.
        rpb_file = data_dir / 'test.RPB'
        self.assertTrue(rpb_file.exists())
        rpb_data = read_file(rpb_file)
        self.assertIsNotNone(rpb_data)

        rpc_file = data_dir / 'test.rpc'
        self.assertTrue(rpc_file.exists())
        rpc_data = read_file(rpc_file)
        self.assertIsNotNone(rpc_data)

        rpctxt_file = data_dir / 'test_rpc.txt'
        self.assertTrue(rpctxt_file.exists())
        rpctxt_data = read_file(rpctxt_file)
        self.assertIsNotNone(rpctxt_data)

        # Each of the read RPC's shall have 16 items in their data
        # dictionariies.
        self.assertEqual(8, len(rpb_data))
        self.assertEqual(8, len(rpc_data))
        self.assertEqual(8, len(rpctxt_data))

        # Check that each RPC has the same set of keys, and that the datatypes are the expected.
        tuple_keys = [
            'IMAGE_OFF',
            'IMAGE_SCALE',
        ]

        for key in tuple_keys:
            self.assertIn(key, rpb_data)
            self.assertIsInstance(rpb_data[key], np.ndarray)
            self.assertEqual(2, len(rpb_data[key]))
            self.assertEqual(rpb_data[key].dtype, np.float64)

            self.assertIn(key, rpc_data)
            self.assertIsInstance(rpc_data[key], np.ndarray)
            self.assertEqual(2, len(rpc_data[key]))
            self.assertEqual(rpc_data[key].dtype, np.float64)

            self.assertIn(key, rpctxt_data)
            self.assertIsInstance(rpctxt_data[key], np.ndarray)
            self.assertEqual(2, len(rpctxt_data[key]))
            self.assertEqual(rpctxt_data[key].dtype, np.float64)

        triple_keys = [
            'GEO_OFF',
            'GEO_SCALE',
        ]

        for key in triple_keys:
            self.assertIn(key, rpb_data)
            self.assertIsInstance(rpb_data[key], np.ndarray)
            self.assertEqual(3, len(rpb_data[key]))
            self.assertEqual(rpb_data[key].dtype, np.float64)

            self.assertIn(key, rpc_data)
            self.assertIsInstance(rpc_data[key], np.ndarray)
            self.assertEqual(3, len(rpc_data[key]))
            self.assertEqual(rpc_data[key].dtype, np.float64)

            self.assertIn(key, rpctxt_data)
            self.assertIsInstance(rpctxt_data[key], np.ndarray)
            self.assertEqual(3, len(rpctxt_data[key]))
            self.assertEqual(rpctxt_data[key].dtype, np.float64)

        array_keys = [
            'LINE_NUM_COEFF',
            'LINE_DEN_COEFF',
            'SAMP_NUM_COEFF',
            'SAMP_DEN_COEFF'
        ]

        for key in array_keys:
            self.assertIn(key, rpb_data)
            self.assertIsInstance(rpb_data[key], np.ndarray)
            self.assertEqual(20, len(rpb_data[key]))
            self.assertEqual(rpb_data[key].dtype, np.float64)

            self.assertIn(key, rpc_data)
            self.assertIsInstance(rpc_data[key], np.ndarray)
            self.assertEqual(20, len(rpc_data[key]))
            self.assertEqual(rpc_data[key].dtype, np.float64)

            self.assertIn(key, rpctxt_data)
            self.assertIsInstance(rpctxt_data[key], np.ndarray)
            self.assertEqual(20, len(rpctxt_data[key]))
            self.assertEqual(rpctxt_data[key].dtype, np.float64)

    def test_file_with_parse_error(self: ReaderTest) -> None:
        data_dir = pathlib.Path(__file__).parent.absolute() / 'data'

        rpb_file = data_dir / 'parse_error.RPB'
        self.assertTrue(rpb_file.exists())

        rpb_data = read_file(rpb_file)
        self.assertIsNone(rpb_data)

    def test_file_with_missing_key(self: ReaderTest) -> None:
        data_dir = pathlib.Path(__file__).parent.absolute() / 'data'

        rpctxt_file = data_dir / 'missing_key_rpc.txt'
        self.assertTrue(rpctxt_file.exists())

        rpctxt_data = read_file(rpctxt_file)
        self.assertIsNone(rpctxt_data)

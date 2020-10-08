import unittest

from dlg.common.reproducibility.constants import PROTOCOL_VERSION
from dlg.common.reproducibility.reproducibility import accumulate_meta_data


class TestMetaData(unittest.TestCase):

    def test_accumulate_meta_data(self):
        expected = {'repro_protocol': PROTOCOL_VERSION, 'hashing_alg': '_sha3.sha3_256'}
        received = accumulate_meta_data()
        self.assertEqual(expected, received)


if __name__ == '__main__':
    unittest.main()

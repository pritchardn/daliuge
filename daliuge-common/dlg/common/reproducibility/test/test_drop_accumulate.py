import json
import unittest

from dlg.common.reproducibility.constants import ReproducibilityFlags
from dlg.common.reproducibility.reproducibility import accumulate_lgt_drop_data, accumulate_lg_drop_data, \
    accumulate_pgt_partition_drop_data, accumulate_pg_drop_data


# TODO: Fix variable naming per function


def load_drop(drop, level):
    drop_dict = drop[level]
    out_dict = {ReproducibilityFlags.RERUN: drop[level + "_rr"],
                ReproducibilityFlags.REPEAT: drop[level + "_rt"],
                ReproducibilityFlags.REPRODUCE: drop[level + "_rp"],
                ReproducibilityFlags.REPLICATE_SCI: drop[level + "_rpl_sci"],
                ReproducibilityFlags.REPLICATE_COMP: drop[level + "_rpl_comp"]}
    return drop_dict, out_dict


class TestLGTDropAccumulate(unittest.TestCase):

    def test_accumulate_lgt_application(self):
        with open("./drops/lga.json", 'r') as handle:
            drop = json.load(handle)
        lga, lgt_a_out = load_drop(drop, "lgt")
        for flag, expected in lgt_a_out.items():
            actual = accumulate_lgt_drop_data(lga, flag)
            self.assertEqual(actual, expected)

    def test_accumulate_lgt_data(self):
        with open("./drops/lgd.json", 'r') as handle:
            drop = json.load(handle)
        lgd, lgt_d_out = load_drop(drop, "lgt")
        for flag, expected in lgt_d_out.items():
            actual = accumulate_lgt_drop_data(lgd, flag)
            self.assertEqual(actual, expected)

    def test_accumulate_lgt_group(self):
        with open("./drops/lgg.json", 'r') as handle:
            drop = json.load(handle)
        lgg, lgt_g_out = load_drop(drop, "lgt")
        for flag, expected in lgt_g_out.items():
            actual = accumulate_lgt_drop_data(lgg, flag)
            self.assertEqual(actual, expected)


class TestLGDropAccumulate(unittest.TestCase):

    def test_accumulate_lg_application(self):
        with open("./drops/lga.json", 'r') as handle:
            drop = json.load(handle)
        lga, lgt_a_out = load_drop(drop, "lg")
        for flag, expected in lgt_a_out.items():
            actual = accumulate_lg_drop_data(lga, flag)
            self.assertEqual(actual, expected)

    def test_accumulate_lg_data(self):
        with open("./drops/lgd.json", 'r') as handle:
            drop = json.load(handle)
        lgd, lgt_d_out = load_drop(drop, "lg")
        for flag, expected in lgt_d_out.items():
            actual = accumulate_lg_drop_data(lgd, flag)
            self.assertEqual(actual, expected)

    def test_accumulate_lg_group(self):
        with open("./drops/lgg.json", 'r') as handle:
            drop = json.load(handle)
        lgg, lgt_g_out = load_drop(drop, "lg")
        for flag, expected in lgt_g_out.items():
            actual = accumulate_lg_drop_data(lgg, flag)
            self.assertEqual(actual, expected)


class TestPGTDropAccumulate(unittest.TestCase):

    def test_accumulate_pgt_application(self):
        with open("./drops/lga.json", 'r') as handle:
            drop = json.load(handle)
        lga, lgt_a_out = load_drop(drop, "pgt")
        for flag, expected in lgt_a_out.items():
            lga['reprodata']['rmode'] = str(flag.value)
            actual = accumulate_pgt_partition_drop_data(lga)
            self.assertEqual(actual, expected)

    def test_accumulate_pgt_data(self):
        with open("./drops/lgd.json", 'r') as handle:
            drop = json.load(handle)
        lgd, lgt_d_out = load_drop(drop, "pgt")
        for flag, expected in lgt_d_out.items():
            lgd['reprodata']['rmode'] = str(flag.value)
            actual = accumulate_pgt_partition_drop_data(lgd)
            self.assertEqual(actual, expected)

    def test_accumulate_pgt_group(self):
        with open("./drops/lgg.json", 'r') as handle:
            drop = json.load(handle)
        lgg, lgt_g_out = load_drop(drop, "pgt")
        for flag, expected in lgt_g_out.items():
            lgg['reprodata']['rmode'] = str(flag.value)
            actual = accumulate_pgt_partition_drop_data(lgg)
            self.assertEqual(actual, expected)


class TestPGDropAccumulate(unittest.TestCase):

    def test_accumulate_pg_application(self):
        with open("./drops/lga.json", 'r') as handle:
            drop = json.load(handle)
        lga, lgt_a_out = load_drop(drop, "pg")
        for flag, expected in lgt_a_out.items():
            lga['reprodata']['rmode'] = str(flag.value)
            actual = accumulate_pg_drop_data(lga)
            self.assertEqual(actual, expected)

    def test_accumulate_pg_data(self):
        with open("./drops/lgd.json", 'r') as handle:
            drop = json.load(handle)
        lgd, lgt_d_out = load_drop(drop, "pg")
        for flag, expected in lgt_d_out.items():
            lgd['reprodata']['rmode'] = str(flag.value)
            actual = accumulate_pg_drop_data(lgd)
            self.assertEqual(actual, expected)

    def test_accumulate_pg_group(self):
        with open("./drops/lgg.json", 'r') as handle:
            drop = json.load(handle)
        lgg, lgt_g_out = load_drop(drop, "pg")
        for flag, expected in lgt_g_out.items():
            lgg['reprodata']['rmode'] = str(flag.value)
            actual = accumulate_pg_drop_data(lgg)
            self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()

import json
import unittest

from dlg.common.reproducibility.constants import ReproducibilityFlags
from dlg.common.reproducibility.reproducibility import init_lgt_repro_data, lg_build_blockdag, init_lg_repro_drop_data


def load_graph(graph):
    with open(graph, 'r') as handle:
        graph = json.load(handle)
    return graph


def process_graph(graph, level: ReproducibilityFlags):
    lgt = init_lgt_repro_data(graph, str(level.value))
    for drop in lgt['nodeDataArray']:
        init_lg_repro_drop_data(drop)
    return lg_build_blockdag(lgt)


class TestLGBuildBlockDAG(unittest.TestCase):

    def test_singlecomponent(self):
        lgt = load_graph('./graphs/singlecomponent.graph')
        expected_visited = [-1]
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_chain(self):
        lgt = load_graph('./graphs/chain.graph')
        expected_visited = [-1, -2, -3]
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_cycle(self):
        graph = load_graph('./graphs/cycle.graph')
        with self.assertRaises(Exception):
            process_graph(graph, ReproducibilityFlags.RERUN)
        with self.assertRaises(Exception):
            process_graph(graph, ReproducibilityFlags.REPRODUCE)

    def test_split(self):
        lgt = load_graph('./graphs/split.graph')
        expected_visited = [-1, -3, -2]
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_transitive(self):
        lgt = load_graph('./graphs/transitive.graph')
        expected_visited = [-1, -2, -3]
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_multichain(self):
        lgt = load_graph('./graphs/multi-chain.graph')
        expected_visited = [-3, -4, -1, -2]
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_bidirectional(self):
        lgt = load_graph('./graphs/bidirectional.graph')
        with self.assertRaises(Exception):
            process_graph(lgt, ReproducibilityFlags.RERUN)
        with self.assertRaises(Exception):
            process_graph(lgt, ReproducibilityFlags.REPRODUCE)

    def test_scatter(self):
        lgt = load_graph('./graphs/scatter_test.graph')
        expected_visited = [-1, -3, -2, -4, -5]
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph(lgt, flag)
            self.assertEqual(expected_visited, visited)

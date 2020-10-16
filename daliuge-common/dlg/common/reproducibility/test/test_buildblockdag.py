import copy
import json
import unittest

from dlg.common.reproducibility.constants import ReproducibilityFlags
from dlg.common.reproducibility.reproducibility import init_lgt_repro_data, init_lg_repro_data, \
    init_pgt_unroll_repro_drop_data, init_pgt_partition_repro_drop_data, build_blockdag, init_pgt_unroll_repro_data, \
    init_pg_repro_drop_data, init_pgt_partition_repro_data
from dlg.dropmake.pg_generator import unroll, partition, resource_map


def load_graph(graph):
    with open(graph, 'r') as handle:
        graph = json.load(handle)
    return graph


def process_graph(graph, level: ReproducibilityFlags):
    lgt = init_lgt_repro_data(graph, str(level.value))
    lg = init_lg_repro_data(lgt)
    pgt = unroll(lg, oid_prefix='1')
    reprodata = pgt.pop()
    for drop in pgt:
        init_pgt_unroll_repro_drop_data(drop)
    sigs, visited = build_blockdag(pgt, 'pgt')
    pgt.append(reprodata)
    return sigs, visited


def process_graph_partition(graph, level: ReproducibilityFlags):
    lgt = init_lgt_repro_data(graph, str(level.value))
    lg = init_lg_repro_data(lgt)
    pgt = unroll(lg, oid_prefix='1')
    pgt = init_pgt_unroll_repro_data(pgt)
    reprodata = pgt.pop()
    pgt = partition(pgt, algo='metis')
    for drop in pgt:
        init_pgt_partition_repro_drop_data(drop)
    sigs, visited = build_blockdag(pgt, 'pgt')
    pgt.append(reprodata)
    return sigs, visited


def process_graph_pg(graph, level: ReproducibilityFlags):
    lgt = init_lgt_repro_data(graph, str(level.value))
    lg = init_lg_repro_data(lgt)
    pgt = unroll(lg, oid_prefix='1')
    init_pgt_unroll_repro_data(pgt)
    reprodata = pgt.pop()
    pgt = partition(pgt, algo='metis')
    pgt.append(reprodata)
    pgt = init_pgt_partition_repro_data(pgt)
    nodes = ['127.0.0.1', '127.0.0.1']
    reprodata = pgt.pop()
    pg = resource_map(pgt, nodes, num_islands=1)
    for drop in pg:
        init_pg_repro_drop_data(drop)
    sigs, visited = build_blockdag(pg, 'pg')
    pg.append(reprodata)
    return sigs, visited


class TestPGTUnrollBuildBlockDAG(unittest.TestCase):

    def test_singlecomponent(self):
        lgt = load_graph('./graphs/singlecomponent.graph')
        expected_visited = ['1_-1_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_chain(self):
        lgt = load_graph('./graphs/chain.graph')
        expected_visited = ['1_-1_0', '1_-2_0', '1_-3_0']
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
        expected_visited = ['1_-1_0', '1_-3_0', '1_-2_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_transitive(self):
        lgt = load_graph('./graphs/transitive.graph')
        expected_visited = ['1_-1_0', '1_-2_0', '1_-3_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_multichain(self):
        lgt = load_graph('./graphs/multi-chain.graph')
        expected_visited = ['1_-3_0', '1_-4_0', '1_-1_0', '1_-2_0']
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
        expected_visited = ['1_-1_0', '1_-3_0/3', '1_-3_0/2', '1_-3_0/1', '1_-3_0/0', '1_-2_0/3', '1_-4_0/3',
                            '1_-2_0/2', '1_-4_0/2', '1_-2_0/1', '1_-4_0/1', '1_-2_0/0', '1_-4_0/0', '1_-5_0']
        for flag in ReproducibilityFlags:
            graph = copy.deepcopy(lgt)
            sigs, visited = process_graph(graph, flag)
            self.assertEqual(expected_visited, visited)


class TestPGTPartitionBuildBlockDAG(unittest.TestCase):

    def test_singlecomponent(self):
        lgt = load_graph('./graphs/singlecomponent.graph')
        expected_visited = ['1_-1_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph_partition(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_chain(self):
        lgt = load_graph('./graphs/chain.graph')
        expected_visited = ['1_-1_0', '1_-2_0', '1_-3_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph_partition(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_cycle(self):
        graph = load_graph('./graphs/cycle.graph')
        with self.assertRaises(Exception):
            process_graph_partition(graph, ReproducibilityFlags.RERUN)
        with self.assertRaises(Exception):
            process_graph_partition(graph, ReproducibilityFlags.REPRODUCE)

    def test_split(self):
        lgt = load_graph('./graphs/split.graph')
        expected_visited = ['1_-1_0', '1_-3_0', '1_-2_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph_partition(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_transitive(self):
        lgt = load_graph('./graphs/transitive.graph')
        expected_visited = ['1_-1_0', '1_-2_0', '1_-3_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph_partition(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_multichain(self):
        lgt = load_graph('./graphs/multi-chain.graph')
        expected_visited = ['1_-3_0', '1_-4_0', '1_-1_0', '1_-2_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph_partition(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_bidirectional(self):
        lgt = load_graph('./graphs/bidirectional.graph')
        with self.assertRaises(Exception):
            process_graph_partition(lgt, ReproducibilityFlags.RERUN)
        with self.assertRaises(Exception):
            process_graph_partition(lgt, ReproducibilityFlags.REPRODUCE)

    def test_scatter(self):
        lgt = load_graph('./graphs/scatter_test.graph')
        expected_visited = ['1_-1_0', '1_-3_0/3', '1_-3_0/2', '1_-3_0/1', '1_-3_0/0', '1_-2_0/3', '1_-4_0/3',
                            '1_-2_0/2', '1_-4_0/2', '1_-2_0/1', '1_-4_0/1', '1_-2_0/0', '1_-4_0/0', '1_-5_0']
        for flag in ReproducibilityFlags:
            graph = copy.deepcopy(lgt)
            sigs, visited = process_graph_partition(graph, flag)
            self.assertEqual(expected_visited, visited)


class TestPGBuildBlockDAG(unittest.TestCase):

    def test_singlecomponent(self):
        lgt = load_graph('./graphs/singlecomponent.graph')
        expected_visited = ['1_-1_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph_pg(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_chain(self):
        lgt = load_graph('./graphs/chain.graph')
        expected_visited = ['1_-1_0', '1_-2_0', '1_-3_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph_pg(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_cycle(self):
        graph = load_graph('./graphs/cycle.graph')
        with self.assertRaises(Exception):
            process_graph_pg(graph, ReproducibilityFlags.RERUN)
        with self.assertRaises(Exception):
            process_graph_pg(graph, ReproducibilityFlags.REPRODUCE)

    def test_split(self):
        lgt = load_graph('./graphs/split.graph')
        expected_visited = ['1_-1_0', '1_-3_0', '1_-2_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph_pg(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_transitive(self):
        lgt = load_graph('./graphs/transitive.graph')
        expected_visited = ['1_-1_0', '1_-2_0', '1_-3_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph_pg(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_multichain(self):
        lgt = load_graph('./graphs/multi-chain.graph')
        expected_visited = ['1_-3_0', '1_-4_0', '1_-1_0', '1_-2_0']
        for flag in ReproducibilityFlags:
            sigs, visited = process_graph_pg(lgt, flag)
            self.assertEqual(expected_visited, visited)

    def test_bidirectional(self):
        lgt = load_graph('./graphs/bidirectional.graph')
        with self.assertRaises(Exception):
            process_graph_pg(lgt, ReproducibilityFlags.RERUN)
        with self.assertRaises(Exception):
            process_graph_pg(lgt, ReproducibilityFlags.REPRODUCE)

    def test_scatter(self):
        lgt = load_graph('./graphs/scatter_test.graph')
        expected_visited = ['1_-1_0', '1_-3_0/3', '1_-3_0/2', '1_-3_0/1', '1_-3_0/0', '1_-2_0/3', '1_-4_0/3',
                            '1_-2_0/2', '1_-4_0/2', '1_-2_0/1', '1_-4_0/1', '1_-2_0/0', '1_-4_0/0', '1_-5_0']
        for flag in ReproducibilityFlags:
            graph = copy.deepcopy(lgt)
            sigs, visited = process_graph_pg(graph, flag)
            self.assertEqual(expected_visited, visited)


if __name__ == '__main__':
    unittest.main()

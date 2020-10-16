import copy
import json
import unittest

from dlg.common.reproducibility.constants import ReproducibilityFlags
from dlg.common.reproducibility.reproducibility import init_lgt_repro_data, init_lg_repro_data, \
    build_blockdag, init_pgt_unroll_repro_data, \
    init_pg_repro_drop_data, init_pgt_partition_repro_data, agglomerate_leaves
from dlg.dropmake.pg_generator import unroll, partition, resource_map

testflags = [ReproducibilityFlags.RERUN, ReproducibilityFlags.REPEAT, ReproducibilityFlags.REPRODUCE,
             ReproducibilityFlags.REPLICATE_SCI, ReproducibilityFlags.REPLICATE_COMP]


def load_graph(graph):
    with open(graph, 'r') as handle:
        graph = json.load(handle)
    return graph


def process_graph(graph, level: ReproducibilityFlags):
    lgt = init_lgt_repro_data(graph, str(level.value))
    lg = init_lg_repro_data(lgt)
    pgt = unroll(lg, oid_prefix='1')
    init_pgt_unroll_repro_data(pgt)
    reprodata = pgt.pop()
    pgt = partition(pgt, algo='metis')
    pgt.append(reprodata)
    pgt = init_pgt_partition_repro_data(pgt)
    nodes = ['127.0.0.1', '127.0.0.1']
    pgt.pop()
    pg = resource_map(pgt, nodes, num_islands=1)
    for drop in pg:
        init_pg_repro_drop_data(drop)
    sigs, visited = build_blockdag(pg, 'pg')
    signature = agglomerate_leaves(sigs)
    return signature


def check_sigs_unique(sigs: dict):
    return len(sigs.values()) == len(set(sigs.values()))


def check_sigs_application_only(sigs: dict):
    flag = True
    if sigs[ReproducibilityFlags.RERUN] != sigs[ReproducibilityFlags.REPLICATE_SCI]:
        flag = False
    if sigs[ReproducibilityFlags.REPEAT] != sigs[ReproducibilityFlags.REPLICATE_COMP]:
        flag = False
    if (sigs[ReproducibilityFlags.REPRODUCE] == sigs[ReproducibilityFlags.RERUN]) \
            or sigs[ReproducibilityFlags.REPRODUCE] == sigs[ReproducibilityFlags.REPEAT]:
        flag = False
    return flag


def check_sigs_changepg(sigs1: dict, sigs2: dict):
    flag = True
    if sigs1[ReproducibilityFlags.RERUN] != sigs2[ReproducibilityFlags.RERUN]:
        flag = False
    if sigs1[ReproducibilityFlags.REPEAT] == sigs2[ReproducibilityFlags.REPEAT]:
        flag = False
    if sigs1[ReproducibilityFlags.REPRODUCE] != sigs2[ReproducibilityFlags.REPRODUCE]:
        flag = False
    if sigs1[ReproducibilityFlags.REPLICATE_SCI] == sigs2[ReproducibilityFlags.REPLICATE_SCI]:
        flag = False
    if sigs1[ReproducibilityFlags.REPLICATE_COMP] == sigs2[ReproducibilityFlags.REPLICATE_COMP]:
        flag = False
    return flag


class TestFullGraphReproducibility(unittest.TestCase):

    def test_singlecomponent(self):
        lgt = load_graph('./graphs/singlecomponent.graph')
        sigs = {}
        for flag in testflags:
            graph = copy.deepcopy(lgt)
            signature = process_graph(graph, flag)
            sigs[flag] = signature
        self.assertTrue(check_sigs_application_only(sigs))

    def test_chain(self):
        lgt = load_graph('./graphs/chain.graph')
        sigs = {}
        for flag in testflags:
            graph = copy.deepcopy(lgt)
            signature = process_graph(graph, flag)
            sigs[flag] = signature
        self.assertTrue(check_sigs_unique(sigs))

    def test_cycle(self):
        graph = load_graph('./graphs/cycle.graph')
        with self.assertRaises(Exception):
            process_graph(graph, ReproducibilityFlags.RERUN)
        with self.assertRaises(Exception):
            process_graph(graph, ReproducibilityFlags.REPRODUCE)

    def test_split(self):
        lgt = load_graph('./graphs/split.graph')
        sigs = {}
        for flag in testflags:
            graph = copy.deepcopy(lgt)
            signature = process_graph(graph, flag)
            sigs[flag] = signature
        self.assertTrue(check_sigs_application_only(sigs))

    def test_transitive(self):
        lgt = load_graph('./graphs/transitive.graph')
        sigs = {}
        for flag in testflags:
            graph = copy.deepcopy(lgt)
            signature = process_graph(graph, flag)
            sigs[flag] = signature
        self.assertTrue(check_sigs_application_only(sigs))

    def test_multichain(self):
        lgt = load_graph('./graphs/multi-chain.graph')
        sigs = {}
        for flag in testflags:
            graph = copy.deepcopy(lgt)
            signature = process_graph(graph, flag)
            sigs[flag] = signature
        self.assertTrue(check_sigs_application_only(sigs))

    def test_bidirectional(self):
        lgt = load_graph('./graphs/bidirectional.graph')
        with self.assertRaises(Exception):
            process_graph(lgt, ReproducibilityFlags.RERUN)
        with self.assertRaises(Exception):
            process_graph(lgt, ReproducibilityFlags.REPRODUCE)

    def test_scatter(self):
        sigs = {}
        lgt = load_graph('./graphs/scatter_test.graph')
        for flag in testflags:
            graph = copy.deepcopy(lgt)
            signature = process_graph(graph, flag)
            sigs[flag] = signature
        self.assertTrue(check_sigs_unique(sigs))

    def test_scatter_change_pg(self):
        sigs = {}
        lgt = load_graph('./graphs/scatter_test.graph')
        for flag in testflags:
            graph = copy.deepcopy(lgt)
            signature = process_graph(graph, flag)
            sigs[flag] = signature
        lgt['nodeDataArray'][0]['fields'][0]['value'] = "2"  # Changing level of scatter
        sigs2 = {}
        for flag in testflags:
            graph = copy.deepcopy(lgt)
            signature = process_graph(graph, flag)
            sigs2[flag] = signature
        self.assertTrue(check_sigs_changepg(sigs, sigs2))


if __name__ == '__main__':
    unittest.main()

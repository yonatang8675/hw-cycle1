import pytest
from cycle1 import has_cycle1, WeightedDiGraph
from testcases import parse_testcases
import random, time, networkx as nx

testcases = parse_testcases("testcases.txt")

def run_testcase(input:str):
    graph = WeightedDiGraph(*input)
    return has_cycle1(graph)
    

testcase_ids = []
for testcase in testcases:
    testcase_ids.append(testcase["name"])

@pytest.mark.parametrize("testcase", testcases, ids=testcase_ids)
def test_cases(testcase):
    actual_output = run_testcase(testcase["input"])
    assert actual_output == testcase["output"], f"Expected {testcase['output']}, got {actual_output}"


# no nodes, no cycle
def test_empty():
    assert has_cycle1(WeightedDiGraph()) == False

# self-loop: cycle product is just the one weight
def test_self_loop():
    assert has_cycle1(WeightedDiGraph([0, 0, 0.5])) == True
    assert has_cycle1(WeightedDiGraph([0, 0, 1.0])) == False
    assert has_cycle1(WeightedDiGraph([0, 0, 2.0])) == False

# two-node cycle, product of both weights
def test_two_node_cycle():
    assert has_cycle1(WeightedDiGraph([0, 1, 0.6], [1, 0, 0.7])) == True   # 0.42
    assert has_cycle1(WeightedDiGraph([0, 1, 2.0], [1, 0, 3.0])) == False  # 6.0
    assert has_cycle1(WeightedDiGraph([0, 1, 0.5], [1, 0, 2.0])) == False  # exactly 1

# 3-node cycle
def test_triangle():
    assert has_cycle1(WeightedDiGraph([0, 1, 0.5], [1, 2, 0.5], [2, 0, 0.5])) == True   # 0.125
    assert has_cycle1(WeightedDiGraph([0, 1, 2.0], [1, 2, 2.0], [2, 0, 2.0])) == False  # 8

# two cycles, one ok and one bad
def test_multiple_cycles():
    # both cycles ok
    assert has_cycle1(WeightedDiGraph([0, 1, 2.0], [1, 0, 2.0], [1, 2, 3.0], [2, 1, 3.0])) == False
    # one bad cycle
    assert has_cycle1(WeightedDiGraph([0, 1, 2.0], [1, 0, 2.0], [1, 2, 0.5], [2, 1, 0.5])) == True

# bad cycle in one disconnected component
def test_disconnected():
    # bad cycle in second component
    assert has_cycle1(WeightedDiGraph([0, 1, 0.1], [2, 3, 0.5], [3, 2, 0.5])) == True
    # all cycles ok
    assert has_cycle1(WeightedDiGraph([0, 1, 2.0], [1, 0, 2.0], [2, 3, 2.0], [3, 2, 2.0])) == False

# 10-node ring, just above and just below product = 1
def test_long_ring():
    edges_below = []
    edges_above = []
    for i in range(10):
        edges_below.append([i, (i+1)%10, 0.95])
        edges_above.append([i, (i+1)%10, 1.01])
    assert has_cycle1(WeightedDiGraph(*edges_below)) == True
    assert has_cycle1(WeightedDiGraph(*edges_above)) == False

# one tiny weight makes the product < 1
def test_tiny_edge():
    assert has_cycle1(WeightedDiGraph([0,1,100], [1,2,100], [2,0,0.00001])) == True

# random tests - check against brute force

def rand_graph(n, m, wmin=0.5, wmax=2.0, seed=42):
    rng = random.Random(seed)
    edge_set = set()
    while len(edge_set) < m:
        u = rng.randint(0, n-1)
        v = rng.randint(0, n-1)
        if u != v and (u,v) not in edge_set:
            edge_set.add((u,v))
    result = []
    for u, v in edge_set:
        result.append((u, v, round(rng.uniform(wmin, wmax), 4)))
    return result

def brute_force(edges):
    graph = WeightedDiGraph(*edges)
    for cycle in nx.simple_cycles(graph):
        cycle_product = 1.0
        for i in range(len(cycle)):
            cycle_product *= graph.edges[cycle[i], cycle[(i+1) % len(cycle)]]["weight"]
        if cycle_product < 1 - 1e-9:
            return True
    return False

# compare against brute force on 50 random small graphs
def test_random_vs_brute():
    for seed in range(50):
        rng = random.Random(seed)
        num_nodes = rng.randint(3, 8)
        num_edges = rng.randint(num_nodes, min(num_nodes*(num_nodes-1), num_nodes+5))
        edges = rand_graph(num_nodes, num_edges, 0.3, 3.0, seed=seed)
        assert has_cycle1(WeightedDiGraph(*edges)) == brute_force(edges), f"seed {seed}"

# 1000 nodes, 100k edges, must run in under 1s
def test_perf():
    graph1 = WeightedDiGraph(*rand_graph(1000, 100000, 0.5, 2.0, seed=777))
    start_time = time.time()
    has_cycle1(graph1)
    assert time.time() - start_time < 1.0

    graph2 = WeightedDiGraph(*rand_graph(1000, 100000, 1.01, 5.0, seed=888))
    start_time = time.time()
    has_cycle1(graph2)
    assert time.time() - start_time < 1.0

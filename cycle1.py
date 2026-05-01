# import subprocess, sys
# subprocess.check_call([sys.executable, "-m", "pip", "install", "networkx>=3.4"], stdout=subprocess.DEVNULL)

import networkx as nx, numpy as np
import math
from collections import deque

def WeightedDiGraph(*edges: list[tuple[int,int,float]])->nx.DiGraph:
    """
    A shorthand function for quickly generating a directed graph with weights on the edges

    >>> G = WeightedDiGraph([0,1,55],[1,2,66],[2,0,77])
    >>> G.edges[0,1]
    {'weight': 55}
    """
    return nx.DiGraph( [(u,v,{"weight":w}) for u,v,w in edges])
    

def has_cycle1(graph: nx.DiGraph)->bool:
    """
    return True iff the given graph has a directed cycle in which the product of weights is smaller than 1.

    >>> has_cycle1(WeightedDiGraph())    # empty graph
    False
    >>> has_cycle1(WeightedDiGraph([0,1,55],[1,2,66],[2,0,77]))
    False
    >>> has_cycle1(WeightedDiGraph([0,1,0.55],[1,2,0.66],[2,0,0.77]))
    True
    """
    # take log of weights: product<1 iff sum of logs<0
    # then detect negative cycle with bellman-ford (SPFA variant for speed)

    nodes = list(graph.nodes)
    n = len(nodes)
    if n == 0:
        return False

    # map node labels to integer indices 0..n-1
    node_index = {}
    for i, v in enumerate(nodes):
        node_index[v] = i

    # build adjacency list using log-weights
    neighbors = []
    for _ in range(n):
        neighbors.append([])
    for u, v, edge_data in graph.edges(data=True):
        neighbors[node_index[u]].append((node_index[v], math.log(edge_data["weight"])))

    # all dists start at 0 (like a virtual source connected to everything)
    dist = []
    in_queue = []
    enqueue_count = []  # if a node is enqueued more than n times -> negative cycle
    for _ in range(n):
        dist.append(0.0)
        in_queue.append(True)
        enqueue_count.append(1)

    queue = deque()
    for i in range(n):
        queue.append(i)

    while queue:
        u = queue.popleft()
        in_queue[u] = False
        for v, w in neighbors[u]:
            if dist[u] + w < dist[v] - 1e-9:
                dist[v] = dist[u] + w
                if not in_queue[v]:
                    enqueue_count[v] += 1
                    if enqueue_count[v] > n:
                        return True  # been relaxed too many times = negative cycle
                    in_queue[v] = True
                    # putting smaller labels first helps performance
                    if queue and dist[v] < dist[queue[0]]:
                        queue.appendleft(v)
                    else:
                        queue.append(v)

    return False


if __name__ == '__main__':
    # edges = eval(input())
    # graph = WeightedDiGraph(*edges)
    # print(has_cycle1(graph))
    import doctest
    print (doctest.testmod())

import csv
import heapq
import pickle
import numpy as np
from collections import namedtuple
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))


DijkState = namedtuple('AlgorithmState', ['current_node', 'visited', 'current_path', 'processing_edge', 'distances', 'previous'])


class DijkstraSimulator:
    def __init__(self, graph, start_node=(24,8), end_node=(24,56)):
        self.graph = graph
        self.visited = set()
        self.current_path = []
        self.processing_edge = None
        self.current_node = start_node
        self.end_node = end_node
        self.reset()


    def reset(self):
        self.distances = {node: np.inf for node in self.graph}
        self.distances[self.current_node] = 0
        self.previous = {node: None for node in self.graph}

        # The same as __init__
        self.visited = set()
        self.current_path = []
        self.processing_edge = None

        self.pq = [(0, self.current_node)]

    def get_state(self):
        return DijkState(
            current_node=self.current_node,
            visited=self.visited,
            current_path=self.current_path,
            processing_edge=self.processing_edge,
            distances=self.distances,
            previous=self.previous
        )
            

    def step(self):
        # print("stepping")
        if not self.pq:
            return None # if there is no more nodes to visit, return None
        current_distance, current_node = heapq.heappop(self.pq)
        if current_node in self.visited:
            return self.get_state()

        self.current_node = current_node
        self.visited.add(current_node)

        if current_node == self.end_node:
            # Reconstruct path
            path = []
            current = current_node
            while current is not None:
                path.append(current)
                current = self.previous[current]
            self.current_path = path[::-1]
            print(self.current_path)
            print("Path found")
            return self.get_state()

        # Process neighbors
        for neighbor, weight in self.graph[current_node]:
            if neighbor not in self.visited:
                self.processing_edge = (current_node, neighbor)
                distance = current_distance + weight
                if distance < self.distances[neighbor]:
                    self.distances[neighbor] = distance
                    self.previous[neighbor] = current_node
                    heapq.heappush(self.pq, (distance, neighbor))

        return self.get_state()

def get_stat_weight(graph):
    weight_list = []
    for start, edges in graph.items():
        for end, weight in edges:
            weight_list.append(weight)

    deviation = np.std(weight_list)
    mean = np.mean(weight_list)

    # print(f"Max weight: {max_weight}")
    # print(f"Min weight: {min_weight}")
    # print(f"Mean weight: {mean}")
    # print(f"Standard deviation: {deviation}")
    # print()
    return (mean, deviation)

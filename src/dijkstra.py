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


graph = {
    # Original core nodes
    (24, 8): [((32, 16), 7), ((16, 16), 6)],
    (16, 16): [((24, 24), 5), ((40, 20), 11)],
    (32, 16): [((24, 24), 8), ((40, 20), 4)],
    (24, 24): [((32, 32), 6), ((48, 24), 10)],
    (40, 20): [((48, 24), 7), ((32, 32), 9)],
    (48, 24): [((40, 32), 5), ((56, 24), 4)],
    (32, 32): [((40, 32), 4), ((24, 44), 6), ((32, 40), 7)],  # Adjusted
    (40, 32): [((32, 40), 7)],
    (24, 44): [((32, 40), 5), ((16, 48), 12), ((40, 32), 8)],  # Adjusted
    (32, 40): [((40, 48), 8), ((16, 48), 12)],
    (16, 48): [((24, 56), 7)],
    (40, 48): [((24, 56), 9)],
    (24, 56): [],
    
    # New left side nodes
    (8, 12): [((16, 16), 5), ((12, 24), 8)],
    (12, 24): [((24, 24), 6), ((8, 36), 7), ((32, 32), 11)],
    (8, 36): [((16, 48), 5), ((24, 44), 9), ((32, 40), 12)],  # Adjusted
    
    # New right side nodes
    (52, 12): [((40, 20), 6), ((56, 24), 7)],
    (56, 24): [((48, 24), 4), ((52, 36), 8), ((32, 32), 10)],
    (52, 36): [((40, 32), 6), ((40, 48), 7), ((32, 40), 11)]
}


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

def save_graph_to_csv(graph, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['node1','node2', 'weight'])
        for node1, edges in graph.items():
            for node2, weight in edges:
                writer.writerow([node1, node2, weight])
                # writer.writerow([node2, node1, weight])

def read_graph_from_csv(filename):
    graph = {}
    with open(filename=filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            node1 = eval(row[0])
            node2 = eval(row[1])
            weight = int(row[2])
            if node1 not in graph:
                graph[node1] = []
            if node2 not in graph:
                graph[node2] = []
            graph[node1].append((node2, weight))
            graph[node2].append((node1, weight))
    return graph

def pickle_graph(graph, filename='./assets/graphs/graph1.pkl'):
    with open(filename, 'wb') as file:
        pickle.dump(graph, file)
    
def unpickle_graph(filename='./assets/graphs/graph0.pkl'):
    with open(filename, 'rb') as file:
        graph = pickle.load(file)
    return graph

def get_stat_weight(graph):
    weight_list = []
    for start, edges in graph.items():
        for end, weight in edges:
            weight_list.append(weight)
    max_weight = max(weight_list)
    min_weight = min(weight_list)

    deviation = np.std(weight_list)
    mean = np.mean(weight_list)

    # print(f"Max weight: {max_weight}")
    # print(f"Min weight: {min_weight}")
    # print(f"Mean weight: {mean}")
    # print(f"Standard deviation: {deviation}")
    # print()
    return (mean, deviation)




if __name__ == "__main__":
    pickle_graph(graph)
    read_graph = unpickle_graph()
    print(read_graph)
    get_stat_weight(read_graph)
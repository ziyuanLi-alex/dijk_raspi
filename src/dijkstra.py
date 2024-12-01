import csv
import pickle

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
    (24, 44): [((32, 40), 5), ((16, 48), 6), ((40, 32), 8)],  # Adjusted
    (32, 40): [((40, 48), 8), ((16, 48), 12)],
    (16, 48): [((24, 56), 7)],
    (40, 48): [((24, 56), 9)],
    
    # New left side nodes
    (8, 12): [((16, 16), 5), ((12, 24), 8)],
    (12, 24): [((24, 24), 6), ((8, 36), 7), ((32, 32), 11)],
    (8, 36): [((16, 48), 5), ((24, 44), 9), ((32, 40), 12)],  # Adjusted
    
    # New right side nodes
    (52, 12): [((40, 20), 6), ((56, 24), 7)],
    (56, 24): [((48, 24), 4), ((52, 36), 8), ((32, 32), 10)],
    (52, 36): [((40, 32), 6), ((40, 48), 7), ((32, 40), 11)]
}



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
    
def unpickle_graph(filename='./assets/graphs/graph1.pkl'):
    with open(filename, 'rb') as file:
        graph = pickle.load(file)
    return graph



if __name__ == "__main__":
    pickle_graph(graph)
    read_graph = unpickle_graph()
    print(read_graph)
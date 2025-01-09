import pickle
from collections import deque
import random
import os
from typing import Dict, List, Set, Tuple, Optional, Any
from matplotlib import pyplot as plt
import networkx as nx


class GraphManager:
    def __init__(self, width: int = 64, height: int = 64, step: int = 8, start_node = (0,0), end_node=(64,64)):
        """初始化图结构。

    Args:
        width (int, optional): 图的宽度，默认为 64。
        height (int, optional): 图的高度，默认为 64。
        setp (int, optional): 步长，默认为 8。

    Attributes:
        width (int): 图的宽度。
        height (int): 图的高度。
        step (int): 步长。
        graph (Dict[Tuple[int, int], List[Tuple[Tuple[int, int], float]]]): 图的邻接表表示。
        nodes (Set[Tuple[int, int]]): 图中所有节点的集合。
    """
        self.width = width
        self.height = height
        self.step = step
        self.graph = {}  # 实际初始化
        self.nodes = set()
        self.start_node = start_node
        self.end_node = end_node
        # self.mean_weight = 0
        # self.weight_deviation = 0

    @classmethod
    def load_from_file(cls, filepath: str) -> 'GraphManager':
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Graph file not found: {filepath}")
        
        try: 
            with open(filepath, 'rb') as f:
                data = pickle.load(f)

            if not isinstance(data, dict) or 'graph' not in data:
                raise ValueError("Invalid graph file format")
            
            instance = cls()
            instance.graph = data.get('graph', {})
            instance.nodes = set(instance.graph.keys())
            instance.start_node = data.get('start', (24, 8))
            instance.end_node = data.get('end', (24, 56))
            # instance._calculate_stats()
            return instance
        
        except (pickle.UnpicklingError, EOFError):
            raise ValueError("Invalid pickle file format")
        

    def _generate_nodes(self) -> None:
        """Generate uniformly distributed nodes in a grid pattern."""
        self.nodes = {
            (x, y) 
            for x in range(0, self.width+self.step, self.step)
            for y in range(0, self.height+self.step, self.step)
        }
        self.graph = {node: [] for node in self.nodes}

    def _generate_connections(self,
                            min_connections: int,
                            max_connections: int,
                            min_weight: int,
                            max_weight: int,
                            distance_factor: float) -> None:
        """Generate random connections between nodes within distance constraints."""
        max_distance = self.step * distance_factor
        
        for node in self.nodes:
            x, y = node
            possible_neighbors = []
            
            for other in self.nodes:
                if other == node:
                    continue
                    
                ox, oy = other
                dist = ((ox-x)**2 + (oy-y)**2)**0.5
                
                if self.step <= dist <= max_distance:
                    possible_neighbors.append(other)
            
            if possible_neighbors:
                num_connections = random.randint(min_connections, 
                                              min(max_connections, len(possible_neighbors)))
                selected = random.sample(possible_neighbors, num_connections)
                
                for neighbor in selected:
                    weight = random.randint(min_weight, max_weight)
                    self.graph[node].append((neighbor, weight))

    def ensure_connectivity(self) -> None:
        """Ensure the graph is fully connected by adding necessary edges."""
        def bfs(start: Tuple[int, int]) -> Set[Tuple[int, int]]:
            visited = set()
            queue = deque([start])
            visited.add(start)
            
            while queue:
                node = queue.popleft()
                for neighbor, _ in self.graph[node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            return visited

        # Find all connected components
        unvisited = set(self.nodes)
        components = []
        
        while unvisited:
            start = next(iter(unvisited))
            component = bfs(start)
            components.append(component)
            unvisited -= component

        # Connect components
        for i in range(len(components) - 1):
            comp1 = components[i]
            comp2 = components[i + 1]
            
            # Find closest pair of nodes between components
            node1, node2 = min(
                [(n1, n2) for n1 in comp1 for n2 in comp2],
                key=lambda pair: ((pair[0][0]-pair[1][0])**2 + 
                                (pair[0][1]-pair[1][1])**2)
            )
            
            # Add bidirectional connection
            weight = random.randint(1, 10)
            self.graph[node1].append((node2, weight))
            self.graph[node2].append((node1, weight))

    def validate_path_exists(self) -> bool:
        """Check if a path exists between start and end nodes."""
        visited = set()
        queue = deque([self.start_node])
        visited.add(self.start_node)
        
        while queue:
            node = queue.popleft()
            if node == self.end_node:
                return True
                
            for neighbor, _ in self.graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return False

    def regenerate_until_valid(self, max_attempts: int = 10) -> bool:
        """Regenerate the graph until a valid path exists."""
        for _ in range(max_attempts):
            self._generate_connections(2, 4, 1, 10, 2.5)
            self.ensure_connectivity()
            if self.validate_path_exists():
                return True
        return False

    def generate_new_graph(self, 
                          min_connections: int = 2,
                          max_connections: int = 4,
                          min_weight: int = 1,
                          max_weight: int = 10,
                          distance_factor: float = 2.5) -> None:
        self._generate_nodes()
        self._generate_connections(min_connections, max_connections,
                                 min_weight, max_weight, distance_factor)
        self.ensure_connectivity()
        if not self.validate_path_exists():
            self.regenerate_until_valid()


    def save_to_file(self, filepath: str) -> None:
        """Save the graph to a pickle file."""
        data = {
            'graph': self.graph,
            'start': self.start_node,
            'end': self.end_node
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

    def get_graph(self) -> Dict[Tuple[int, int], List[Tuple[Tuple[int, int], int]]]:
        """Get the graph structure."""
        return self.graph

    def get_endpoints(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Get start and end nodes."""
        return self.start_node, self.end_node

    def set_endpoints(self, 
                     start: Optional[Tuple[int, int]] = None,
                     end: Optional[Tuple[int, int]] = None) -> None:
        """Set start and end nodes."""
        if start is not None and start in self.nodes:
            self.start_node = start
        if end is not None and end in self.nodes:
            self.end_node = end


    def draw_graph(self, 
                   figsize: Tuple[int, int] = (12, 8), 
                   node_size: int = 500, 
                   node_color: str = 'lightblue', 
                   start_color: str = 'green', 
                   end_color: str = 'red', 
                   font_size: int = 10, 
                   font_weight: str = 'bold'):
        """绘制图的结构。"""
        G = nx.Graph()
        for node, edges in self.graph.items():
            for neighbor, weight in edges:
                G.add_edge(node, neighbor, weight=weight)
        
        pos = {node: node for node in G.nodes()}
        labels = nx.get_edge_attributes(G, 'weight')
        
        plt.figure(figsize=figsize)
        nx.draw(G, pos, with_labels=True, node_size=node_size, 
                node_color=node_color, font_size=font_size, 
                font_weight=font_weight)
        nx.draw_networkx_nodes(G, pos, nodelist=[self.start_node], 
                               node_color=start_color, node_size=node_size*1.2)
        nx.draw_networkx_nodes(G, pos, nodelist=[self.end_node], 
                               node_color=end_color, node_size=node_size*1.2)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        plt.show()

def validate_hardcode():
    import networkx as nx
    import matplotlib.pyplot as plt

    graph = {
    # Original core nodes
    (24, 8): [((32, 16), 7), ((16, 16), 6)],
    (16, 16): [((24, 24), 5), ((40, 20), 11)],
    (32, 16): [((24, 24), 8), ((40, 20), 4)],
    (24, 24): [((32, 32), 6), ((48, 24), 10)],
    (40, 20): [((48, 24), 7), ((32, 32), 9)],
    (48, 24): [((40, 32), 5), ((56, 24), 4)],
    (32, 32): [((40, 32), 4), ((24, 44), 6), ((32, 40), 7)],  
    (40, 32): [((32, 40), 7)],
    (24, 44): [((32, 40), 5), ((16, 48), 12), ((40, 32), 8)],  
    (32, 40): [((40, 48), 8), ((16, 48), 12)],
    (16, 48): [((24, 56), 7)],
    (40, 48): [((24, 56), 9)],
    (24, 56): [],
    
    # left side nodes
    (8, 12): [((16, 16), 5), ((12, 24), 8)],
    (12, 24): [((24, 24), 6), ((8, 36), 7), ((32, 32), 11)],
    (8, 36): [((16, 48), 5), ((24, 44), 9), ((32, 40), 12)], 
    
    # right side nodes
    (52, 12): [((40, 20), 6), ((56, 24), 7)],
    (56, 24): [((48, 24), 4), ((52, 36), 8), ((32, 32), 10)],
    (52, 36): [((40, 32), 6), ((40, 48), 7), ((32, 40), 11)]
    }
    
    gm = GraphManager()
    gm.graph = graph
    gm.nodes = set(graph.keys())
    gm.start_node = (24, 8)
    gm.end_node = (24, 56)

    # 保存图到文件 
    gm.save_to_file('./assets/graphs/graph1.pkl')

    # import networkx as nx
    # import matplotlib.pyplot as plt

    with open('./assets/graphs/graph1.pkl', 'rb') as f:
        data = pickle.load(f)
        graph = data['graph']
        start_node = data['start']
        end_node = data['end']

    print(f'Start node: {start_node}, End node: {end_node}')

    G = nx.Graph()

    for node, edges in graph.items():
        for edge in edges:
            G.add_edge(node, edge[0], weight=edge[1])

    pos = {node: node for node in G.nodes()}
    labels = nx.get_edge_attributes(G, 'weight')

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', font_size=10, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()

def validate_generation():
    gm = GraphManager(width=64, height=64, step=8)

    gm.end_node = (64, 64)
    gm.start_node = (0,0)

    # gm._generate_nodes()

    # gm._generate_connections(
    #     min_connections=2,
    #     max_connections=4,
    #     min_weight=1,
    #     max_weight=10,
    #     distance_factor=2.5
    # )

    # gm.ensure_connectivity()

    gm.generate_new_graph(2,4,1,5,2.5)

    # 验证起点到终点有路径
    if gm.validate_path_exists():
        print("图中存在从起点到终点的路径。")
    else:
        print("图中不存在从起点到终点的路径。")

    # 保存图到文件
    gm.save_to_file('./assets/graphs/generated_graph.pkl')

    # 从文件加载图
    loaded_gm = GraphManager.load_from_file('./assets/graphs/generated_graph.pkl')

    # 绘制图
    loaded_gm.draw_graph()






if __name__ == "__main__":
    # validate_hardcode()
    # validate_generation()

    # gm = GraphManager()
    loaded_gm = GraphManager.load_from_file('./assets/graphs/generated_graph.pkl')
    
    loaded_gm.draw_graph()

    print(loaded_gm.graph)

    

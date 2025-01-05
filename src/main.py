import pygame
import time
from collections import namedtuple
from dijkstra import unpickle_graph, get_stat_weight, DijkstraSimulator
from GraphManager import GraphManager

DijkState = namedtuple('AlgorithmState', ['current_node', 'visited', 'current_path', 'processing_edge'])

class GraphVisualizer:
    def __init__(self, graph, start_node, end_node,
                 window_size=(640, 640), grid_size=64):
        pygame.init()
        self.graph = graph
        self.window_size = window_size
        self.grid_size = grid_size
        self.scale = window_size[0] // grid_size
        (self.mean_weight, self.weight_deviation) = get_stat_weight(self.graph)
        self.start_node = start_node
        self.end_node = end_node

        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Dijkstra's Algorithm Visualizer")

        self.path_found = False

        # Colors
        self.BLACK = (0,0,0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 100, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.GRAY = (128, 128, 128)
        self.PURPLE = (147, 0, 211)


    def scale_coordinates(self, x, y):
        """Scale graph coordinates to screen coordinates"""
        return (x * self.scale, y * self.scale)
    
    def draw_edge(self, start, end, weight, color=None, progress=1.0):

        if color is None:
            color = self.WHITE # default color is white

        # Weight Will be used to adjust brightness of the edge.
        brightness = max(0.2, min(1.0, 1.0 - (weight - self.mean_weight) / (2 * self.weight_deviation)))
        color = tuple(int(c * brightness) for c in color)

        start_pos = self.scale_coordinates(*start)
        end_pos = self.scale_coordinates(*end)
        intermediate_pos = None

        if progress < 1.0:
            x = int(start_pos[0] + (end_pos[0] - start_pos[0]) * progress)
            y = int(start_pos[1] + (end_pos[1] - start_pos[1]) * progress)
            intermediate_pos = (x, y)
        
        if intermediate_pos:
            pygame.draw.line(self.screen, color, start_pos, intermediate_pos)
            pygame.draw.line(self.screen, self.GRAY, intermediate_pos, end_pos)
        else:
            pygame.draw.line(self.screen, color, start_pos, end_pos)
        

    def draw_frame(self, algorithm_state):
        self.screen.fill(self.BLACK)

        for start, edges in self.graph.items():
            for end, weight in edges:
                if algorithm_state.processing_edge == (start, end):
                    continue
                self.draw_edge(start, end, weight, self.WHITE)

        if algorithm_state.current_path:
            path = algorithm_state.current_path
            for i in range(len(path) - 1):
                self.draw_edge(path[i], path[i+1], 0, self.PURPLE)
            self.path_found = True
            
        for node in self.graph:
            if node == self.start_node:
                color = self.GREEN
            elif node == self.end_node:
                color = self.RED
            elif node == algorithm_state.current_node:
                color = self.YELLOW
            elif node in algorithm_state.visited:
                color = self.PURPLE
            else:
                color = self.BLUE
            pygame.draw.circle(self.screen, color, self.scale_coordinates(*node), 4)

        if algorithm_state.processing_edge:
            start, end = algorithm_state.processing_edge
            if not self.path_found:
                # 动画显示正在处理的边
                for i in range(0, 101, 3):
                    progress = i / 100.0
                    self.draw_edge(start, end, 0, self.YELLOW, progress=progress)
                    pygame.display.flip()
                    time.sleep(1/120)
            else:
                # 如果这条边是路径的一部分，用紫色绘制
                if algorithm_state.current_path and \
                any(p1 == start and p2 == end for p1, p2 in zip(algorithm_state.current_path[:-1], algorithm_state.current_path[1:])):
                    self.draw_edge(start, end, 0, self.PURPLE)
                else:
                    self.draw_edge(start, end, 0, self.WHITE)

        pygame.display.flip()


        
        
        
def main():
    # 图结构
    try:
        graph_manager = GraphManager.load_from_file("./assets/graphs/generated_graph.pkl")
    except (FileNotFoundError, ValueError):
        print("No graph found, generating new graph")
        graph_manager = GraphManager()
        graph_manager.generate_new_graph()
        graph_manager.save_to_file("./assets/graphs/generated_graph.pkl")
    
    graph = graph_manager.get_graph()
    start_node, end_node = graph_manager.get_endpoints()
    
    visualizer = GraphVisualizer(
        graph=graph,
        start_node=start_node,
        end_node=end_node
    )
    simulator = DijkstraSimulator(
        graph=graph,
        start_node=start_node,
        end_node=end_node
    )

    # 主循环
    clock = pygame.time.Clock()
    running = True
    paused = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused

        if not paused:
            state = simulator.step()
            if state:
                visualizer.draw_frame(state)
            
        clock.tick(120)  #  120 FPS

    pygame.quit()


if __name__ == "__main__":
    main()


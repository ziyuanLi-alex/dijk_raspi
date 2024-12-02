import pygame
import time
from collections import namedtuple
from dijkstra import unpickle_graph, get_stat_weight, DijkstraSimulator
import colorsys

DijkState = namedtuple('AlgorithmState', ['current_node', 'visited', 'current_path', 'processing_edge'])

class GraphVisualizer:
    def __init__(self, graph, window_size=(640, 640), grid_size=64):
        pygame.init()
        self.graph = graph
        self.window_size = window_size
        self.grid_size = grid_size
        self.scale = window_size[0] // grid_size
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Dijkstra's Algorithm Visualizer")
        (self.mean_weight, self.weight_deviation) =  get_stat_weight(self.graph)
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
    
    def draw_grid(self):
        """Draw grid lines, we need 64x64 intersections"""
        for x in range(0, self.window_size[0], self.scale):
            # 0, 10 ... 640
            pygame.draw.line(self.screen, self.GRAY, (x, 0), (x, self.window_size[1])) 
        for y in range(0, self.window_size[1], self.scale):
            pygame.draw.line(self.screen, self.GRAY, (0, y), (self.window_size[0], y))
    
    def draw_edge(self, start, end, weight, color=None, progress=1.0):

        if color is None:
            color = self.WHITE # default color is white

        # weight is now a dummy variable. Will be used to adjust brightness of the edge.
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
        # self.draw_grid()

        for start,edges in self.graph.items():
            for end,weight in edges:
                if algorithm_state.processing_edge == (start, end):
                    continue # we draw the "background edges" first and do the animations later in another for loop.
                # color = self.PURPLE if algorithm_state.current_path and \
                #        any(p1 == start and p2 == end for p1, p2 in zip(algorithm_state.current_path[:-1], algorithm_state.current_path[1:])) \
                #        else self.WHITE
                if algorithm_state.current_path and \
                       any(p1 == start and p2 == end for p1, p2 in zip(algorithm_state.current_path[:-1], algorithm_state.current_path[1:])):
                    color = self.PURPLE
                    self.path_found = True

                else:
                    color = self.WHITE
                self.draw_edge(start, end, weight, color)
        
        
        start_node = (24, 8)
        end_node = (24, 56)

        for node in self.graph:
            if node == start_node:
                color = self.GREEN
            elif node == end_node:
                color = self.RED
            elif node == algorithm_state.current_node:
                color = self.YELLOW
            elif node in algorithm_state.visited:
                color = self.PURPLE
            else:
                color = self.BLUE
            pygame.draw.circle(self.screen, color, self.scale_coordinates(*node), 4)

        # if algorithm_state.current_path:
        #     for start, end in zip(algorithm_state.current_path[:-1], algorithm_state.current_path[1:]):
        #         self.draw_edge(start, end, 0, self.YELLOW)

        if algorithm_state.processing_edge and not self.path_found:
            start, end = algorithm_state.processing_edge
            for i in range (0, 101, 3):
                progress = i / 100.0
                self.draw_edge(start, end, 0, self.YELLOW, progress=progress)
                pygame.display.flip()
                time.sleep(1/120)
        
        if self.path_found:
            start, end = algorithm_state.processing_edge
            self.draw_edge(start, end, 0, self.WHITE)
            pygame.draw.circle(self.screen, self.PURPLE, self.scale_coordinates(*start), 4)
            pygame.draw.circle(self.screen, self.RED, self.scale_coordinates(*end), 4)

        

        pygame.display.flip()
        
def main():
    visualizer = GraphVisualizer(unpickle_graph())
    simulator = DijkstraSimulator(unpickle_graph())
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
                elif event.key == pygame.K_r:
                    simulator.reset()

        if not paused:
            state = simulator.step()
            if state:
                visualizer.draw_frame(state)
            
        clock.tick(120)  #  120 FPS

    pygame.quit()


if __name__ == "__main__":
    main()


import pygame
import time
from collections import namedtuple
from dijkstra import get_stat_weight, DijkstraSimulator

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

        # 探索路径的动画状态
        self.exploring_progress = 0
        self.exploring_speed = 0.5

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
        self.ORANGE = (255, 165, 0)  # 用于显示探索路径

    def draw_exploring_path(self, current_node, previous):
        """绘制正在探索的路径"""
        if not current_node:
            return
            
        # 构建从当前节点到起点的路径
        exploring_path = []
        current = current_node
        while current is not None:
            exploring_path.append(current)
            current = previous.get(current)
        exploring_path.reverse()
        
        # 绘制探索路径
        for i in range(len(exploring_path) - 1):
            self.draw_edge(exploring_path[i], exploring_path[i+1], 0, self.ORANGE)

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

        # 绘制基础图形
        for start, edges in self.graph.items():
            for end, weight in edges:
                if algorithm_state.processing_edge == (start, end):
                    continue
                self.draw_edge(start, end, weight, self.WHITE)

        # 绘制路径
        if algorithm_state.current_path:
            # 如果找到最终路径，绘制最终路径
            path = algorithm_state.current_path
            for i in range(len(path) - 1):
                self.draw_edge(path[i], path[i+1], 0, self.PURPLE)
                pygame.display.flip()
                # time.sleep(0.3)
            # self.draw_final_path(path)
            self.path_found = True
        elif algorithm_state.current_node:
            # 否则绘制探索路径
            self.draw_exploring_path(
                algorithm_state.current_node,
                algorithm_state.previous
            )

        # 绘制节点
        for node in self.graph:
            if node == self.start_node:
                color = self.GREEN
            elif node == self.end_node:
                color = self.RED
            elif node == algorithm_state.current_node:
                color = self.YELLOW
            elif node in algorithm_state.visited:
                color = self.ORANGE if not self.path_found else self.PURPLE
            else:
                color = self.BLUE
            pygame.draw.circle(self.screen, color, self.scale_coordinates(*node), 4)

        # 处理当前正在探索的边
        if algorithm_state.processing_edge:
            start, end = algorithm_state.processing_edge
            if not self.path_found:
                for i in range(0, 101, 20):
                    progress = i / 100.0
                    self.draw_edge(start, end, 0, self.YELLOW, progress=progress)
                    pygame.display.flip()
                    # time.sleep(1/120)
            else:
                if algorithm_state.current_path and \
                any(p1 == start and p2 == end for p1, p2 in zip(algorithm_state.current_path[:-1], algorithm_state.current_path[1:])):
                    self.draw_edge(start, end, 0, self.PURPLE)
                else:
                    self.draw_edge(start, end, 0, self.WHITE)

        pygame.display.flip()

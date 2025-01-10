import pygame
import time
from dijkstra import unpickle_graph, get_stat_weight
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from led_lib.rgbmatrix import RGBMatrix, RGBMatrixOptions


class GraphVisualizer:
    def __init__(self, graph, start_node, end_node,
                 window_size=(640, 640), grid_size=64,
                 padding=10,
                 LED_width=64, LED_height=64):
        pygame.init()
        self.graph = graph
        self.window_size = window_size
        self.grid_size = grid_size
        self.scale = window_size[0] // grid_size
        (self.mean_weight, self.weight_deviation) = get_stat_weight(self.graph)
        self.start_node = start_node
        self.end_node = end_node

        self.padding = padding
        self.drawing_area = (window_size[0] + 2 * padding, 
                           window_size[1] + 2 * padding)
        self.scale = self.drawing_area[0] // grid_size
        self.screen = pygame.display.set_mode(self.drawing_area)
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
        self.ORANGE = (255, 165, 0)  # 用于显示探索路径
        self.WHITE_DIM = (80, 80, 80)  

        # LED矩阵初始化
        self.options = RGBMatrixOptions()
        self.options.rows = 64
        self.options.chain_length = 1
        self.options.parallel = 1
        self.options.rows = 64
        self.options.cols = 64
        self.options.hardware_mapping = 'regular'
        self.matrix = RGBMatrix(options=self.options)

        max_x = max(node[0] for node in graph.keys())
        max_y = max(node[1] for node in graph.keys())
        self.led_scale_x = (self.matrix.width - 4) / max_x
        self.led_scale_y = (self.matrix.height - 4) / max_y

    def draw_edge_LED(self, start, end, color):
        
        """在LED矩阵上绘制边"""

        # if color == self.WHITE:
        #     color == self.WHITE_DIM
    
        x1, y1 = self.scale_coordinates_LED(*start)
        x2, y2 = self.scale_coordinates_LED(*end)
        
        # 使用Bresenham算法绘制线段
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steep = dy > dx
        
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
            
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            
        dx = x2 - x1
        dy = abs(y2 - y1)
        error = dx // 2
        y = y1
        y_step = 1 if y1 < y2 else -1
        
        for x in range(x1, x2 + 1):
            if steep:
                self.matrix.SetPixel(y, x, *color)
            else:
                self.matrix.SetPixel(x, y, *color)
            error -= dy
            if error < 0:
                y += y_step
                error += dx

    def scale_coordinates_LED(self, x, y):
        """将坐标转换为LED矩阵上的坐标"""
        return (int(x*self.led_scale_x+1), int(y*self.led_scale_y+1))
    
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
            self.draw_edge_LED(exploring_path[i], exploring_path[i+1], self.ORANGE)

    
    def draw_node_LED(self, pos, color):

        x, y = self.scale_coordinates_LED(*pos)
        self.matrix.SetPixel(x,y, *color)
        self.matrix.SetPixel(x+1, y, *color)
        self.matrix.SetPixel(x, y+1, *color)
        self.matrix.SetPixel(x+1, y+1, *color)
    
    def scale_coordinates(self, x, y):
        """Scale graph coordinates to screen coordinates"""
        return (x * self.scale + self.padding, y * self.scale + self.padding)
    
    def pygame_to_led_coordinate(self, x, y):
        """将Pygame坐标转换为LED矩阵坐标"""
        # 先转回相对坐标
        graph_x = x / self.scale
        graph_y = y / self.scale
        # 再转为LED坐标
        led_x = int(graph_x * self.led_scale_x + 2)
        led_y = int(graph_y * self.led_scale_y + 2)
        return led_x, led_y

    def draw_led_from_pygame_surface(self):
        """Read pixels from Pygame surface and display to LED matrix"""
        self.matrix.Clear()
        surface_array = pygame.surfarray.pixels3d(self.screen)
        
        # Iterate through the LED matrix
        for led_y in range(self.matrix.height):
            for led_x in range(self.matrix.width):
                pygame_x = int(led_x * self.window_size[0] / self.matrix.width)
                pygame_y = int(led_y * self.window_size[1] / self.matrix.height)
                
                if 0 <= pygame_x < surface_array.shape[0] and 0 <= pygame_y < surface_array.shape[1]:
                    color = surface_array[pygame_x][pygame_y]
                    led_color = tuple(int(c * 0.4) for c in color)
                    self.matrix.SetPixel(led_x, led_y, *led_color)
        
        del surface_array  # Release the surface array

    
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
        if not algorithm_state.current_path:
            self.matrix.Clear() 

        # 绘制基础图形(所有边)
        for start, edges in self.graph.items():
            for end, weight in edges:
                if algorithm_state.processing_edge == (start, end):
                    continue
                self.draw_edge(start, end, weight, self.WHITE)
                self.draw_edge_LED(start, end, self.WHITE_DIM)

        # 路径控制
        if algorithm_state.current_path:
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
                color = self.ORANGE
            else:
                color = self.BLUE
            pygame.draw.circle(self.screen, color, self.scale_coordinates(*node), 4)
            self.draw_node_LED(node, color)

        # 处理当前正在探索的边
        if algorithm_state.processing_edge:
            start, end = algorithm_state.processing_edge
            if not self.path_found:
                for i in range(0, 101, 30):
                    progress = i / 100.0
                    self.draw_edge(start, end, 0, self.YELLOW, progress=progress)
                    self.draw_edge_LED(start, end, self.YELLOW)
                    pygame.display.flip()
                    # time.sleep(1/120)

        if self.path_found:
            # 只绘制最终状态
            path = algorithm_state.current_path
            self.draw_edge(algorithm_state.processing_edge[0], algorithm_state.processing_edge[1], 0, self.WHITE_DIM)
            pygame.display.flip()
            for i in range(len(path) - 1):
                self.draw_edge(path[i], path[i+1], 0, self.PURPLE)
                self.draw_edge_LED(path[i], path[i+1], self.PURPLE)
                pygame.display.flip()
            
            return
        
        # self.draw_led_from_pygame_surface()
        
        pygame.display.flip()

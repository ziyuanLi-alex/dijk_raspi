from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from led_lib.rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
from GraphManager import GraphManager
from dijkstra import DijkstraSimulator

class LEDGraphVisualizer:
    def __init__(self, graph, start_node, end_node, matrix_rows=64, chain_length=1):
        self.options = RGBMatrixOptions()
        self.options.rows = matrix_rows
        self.options.chain_length = chain_length
        self.options.parallel = 1
        self.options.rows = 64
        self.options.cols = 64
        self.options.hardware_mapping = 'regular'

        self.matrix = RGBMatrix(options=self.options)
        self.graph = graph
        self.start_node = start_node
        self.end_node = end_node

         # 计算缩放比例，将图坐标映射到LED矩阵尺寸
        max_x = max(node[0] for node in graph.keys())
        max_y = max(node[1] for node in graph.keys())
        self.scale_x = (self.matrix.width - 4) / max_x  # 留出边距
        self.scale_y = (self.matrix.height - 4) / max_y
        
        # 定义颜色
        self.BLACK = (0, 0, 0)
        self.WHITE = (100, 100, 100)  # 调暗以防止过亮
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.PURPLE = (147, 0, 211)
        self.ORANGE = (255, 165, 0)

    def scale_coordinates(self, x, y):
        """将坐标转换为LED矩阵上的坐标"""
        return (int(x*self.scale_x+1), int(y*self.scale_y+1))

    def draw_node(self, pos, color):

        x, y = self.scale_coordinates(*pos)
        self.matrix.SetPixel(x,y, *color)
        self.matrix.SetPixel(x+1, y, *color)
        self.matrix.SetPixel(x, y+1, *color)
        self.matrix.SetPixel(x+1, y+1, *color)

    def draw_edge(self, start, end, color):
        """在LED矩阵上绘制边"""
        x1, y1 = self.scale_coordinates(*start)
        x2, y2 = self.scale_coordinates(*end)
        
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

    def draw_frame(self, algorithm_state):
        """绘制当前算法状态"""
        # 清空显示
        if not algorithm_state.current_path:
            self.matrix.Clear() 
        
        # 绘制所有边
        for start, edges in self.graph.items():
            for end, weight in edges:
                self.draw_edge(start, end, self.WHITE)
        
        # 绘制已访问路径
        if algorithm_state.current_path:
            path = algorithm_state.current_path
            for i in range(len(path) - 1):
                self.draw_edge(path[i], path[i+1], self.ORANGE)
        elif algorithm_state.current_node and algorithm_state.previous:
            # 绘制探索路径
            current = algorithm_state.current_node
            exploring_path = []
            while current is not None:
                exploring_path.append(current)
                current = algorithm_state.previous.get(current)
            exploring_path.reverse()
            
            for i in range(len(exploring_path) - 1):
                self.draw_edge(exploring_path[i], exploring_path[i+1], self.ORANGE)
        
        # 绘制所有节点
        for node in self.graph:
            if node == self.start_node:
                color = self.GREEN
            elif node == self.end_node:
                color = self.RED
            elif node == algorithm_state.current_node:
                color = self.YELLOW
            elif node in algorithm_state.visited:
                color = self.PURPLE if algorithm_state.current_path else self.ORANGE
            else:
                color = self.BLUE
            self.draw_node(node, color)
        
        # 如果正在处理某条边，特殊显示该边
        if algorithm_state.processing_edge:
            start, end = algorithm_state.processing_edge
            self.draw_edge(start, end, self.YELLOW)

def main():
    # 图结构和算法初始化
    try:
        graph_manager = GraphManager.load_from_file("./assets/graphs/generated_graph.pkl")
    except (FileNotFoundError, ValueError):
        print("No graph found, generating new graph")
        graph_manager = GraphManager()
        graph_manager.generate_new_graph()
        graph_manager.save_to_file("./assets/graphs/generated_graph.pkl")
    
    graph = graph_manager.get_graph()
    start_node, end_node = graph_manager.get_endpoints()
    
    # 创建LED可视化器
    visualizer = LEDGraphVisualizer(
        graph=graph,
        start_node=start_node,
        end_node=end_node,
        matrix_rows=64,  
        chain_length=1
    )
    
    # 创建算法模拟器
    simulator = DijkstraSimulator(
        graph=graph,
        start_node=start_node,
        end_node=end_node
    )

    try:
        print("Press CTRL-C to stop")
        while True:
            state = simulator.step()
            if state:
                visualizer.draw_frame(state)
            time.sleep(0.1)  # 控制更新速度
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()


from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from led_lib.rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
from GraphManager import GraphManager
from dijkstra import DijkstraSimulator

class LEDGraphVisualizer:
    def __init__(self, graph, start_node, end_node, matrix_rows=32, chain_length=1):
        self.options = RGBMatrixOptions()
        self.options.rows = matrix_rows
        self.options.chain_length = chain_length
        self.options.parallel = 1
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
        self.WHITE = (180, 180, 180)  # 调暗以防止过亮
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.PURPLE = (147, 0, 211)
        self.ORANGE = (255, 165, 0)

    def scale_coordinates(self, x, y ):
        """将坐标转换为LED矩阵上的坐标"""
        return (int(x*self.scale_x + 2), int(y*self.scale_y+2))

    def draw_node(self, pos, color):

        x, y = self.scale_coordinates(*pos)
        self.matrix.SetPixel(x,y, *color)
        self.matrix.SetPixel(x+1, y, *color)
        self.matrix.SetPixel(x, y+1, *color)
        self.matrix.SetPixel(x+1, y+1, *color)

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
        matrix_rows=32,  # 根据你的LED矩阵配置调整
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


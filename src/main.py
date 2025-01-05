import pygame
import time
from collections import namedtuple
from dijkstra import unpickle_graph, get_stat_weight, DijkstraSimulator
from GraphManager import GraphManager
from GraphVisualizer import GraphVisualizer

# DijkState = namedtuple('AlgorithmState', ['current_node', 'visited', 'current_path', 'processing_edge'])
DijkState = namedtuple('AlgorithmState', ['current_node', 'visited', 'current_path', 'processing_edge', 'distances', 'previous'])


        
def main():
    # 图结构
    try:
        graph_manager = GraphManager.load_from_file("./assets/graphs/graph2.pkl")
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


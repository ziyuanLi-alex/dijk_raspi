import pygame
import time
import csv

pygame.init()
window_size = (640, 640)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Dijkstra's Algorithm")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
AMBER = (255, 191, 0)

def scale_coordinates(x, y):
    """Scale graph coordinates to screen coordinates"""
    return (x * 10, y * 10)

def draw_graph(current_node=None, path=None, edges_with_weights=[], node_positions=[]):
    screen.fill(BLACK)
    
    # Draw edges
    for (u, v, w) in edges_with_weights:
        start = scale_coordinates(*u)
        end = scale_coordinates(*v)
        pygame.draw.line(screen, WHITE, start, end, 1)
        
    # Draw nodes
    for node in node_positions:
        pos = scale_coordinates(*node)
        color = BLUE
        if node == current_node:
            color = RED
        elif path and node in path:
            color = GREEN
        pygame.draw.circle(screen, color, pos, 4)
    
    pygame.display.flip()

if __name__ == "__main__":
    # Load graph from CSV
    graph = {}
    with open('./assets/graphs/graph1.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
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
    
    # Define start and end nodes
    start_node = (24, 8)
    end_node = (24, 56)
    
    # Extract edges with weights and node positions
    edges_with_weights = []
    node_positions = set()
    for node, neighbors in graph.items():
        node_positions.add(node)
        for neighbor, weight in neighbors:
            edges_with_weights.append((node, neighbor, weight))
            node_positions.add(neighbor)
    
    # Draw the graph
    draw_graph(edges_with_weights=edges_with_weights, node_positions=list(node_positions))
    
    # Keep the window open until closed by the user
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        time.sleep(0.1)
    
    pygame.quit()
    
    
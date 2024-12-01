import pygame
import time
import csv
from dijkstra import unpickle_graph

pygame.init()
WINDOW_SIZE = (640, 640)  
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Dijkstra's Algorithm")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

graph = unpickle_graph()

def scale_coordinates(x, y):
    """Scale graph coordinates to screen coordinates"""
    return (x * 10, y * 10)

def draw_grid():
    """Draw a faint grid"""
    for x in range(0, WINDOW_SIZE[0], 10):
        pygame.draw.line(screen, GRAY, (x, 0), (x, WINDOW_SIZE[1]), 1)
    for y in range(0, WINDOW_SIZE[1], 10):
        pygame.draw.line(screen, GRAY, (0, y), (WINDOW_SIZE[0], y), 1)



def draw_graph():
    """Draw the complete graph"""
    screen.fill(BLACK)
    draw_grid()
    
    # Draw edges and weights
    for start_node, edges in graph.items():
        start_pos = scale_coordinates(*start_node)
        for end_node, weight in edges:
            end_pos = scale_coordinates(*end_node)
            
            # Draw edge
            pygame.draw.line(screen, WHITE, start_pos, end_pos, 2)
            
            # Draw weight
            mid_x = (start_pos[0] + end_pos[0]) // 2
            mid_y = (start_pos[1] + end_pos[1]) // 2
            font = pygame.font.Font(None, 24)
            text = font.render(str(weight), True, WHITE)
            text_rect = text.get_rect(center=(mid_x, mid_y))
            # Add a small black background for better weight visibility
            bg_rect = text_rect.copy()
            bg_rect.inflate_ip(10, 10)
            pygame.draw.rect(screen, BLACK, bg_rect)
            screen.blit(text, text_rect)
    
    # Draw nodes
    for node in graph.keys():
        pos = scale_coordinates(*node)
        # Start node (24, 8)
        if node == (24, 8):
            pygame.draw.circle(screen, GREEN, pos, 6)
        # End node (24, 56)
        elif node == (24, 56):
            pygame.draw.circle(screen, RED, pos, 6)
        # All other nodes
        else:
            pygame.draw.circle(screen, BLUE, pos, 6)
        
        # Draw node coordinates
        # font = pygame.font.Font(None, 20)
        # text = font.render(f"{node}", True, WHITE)
        # text_rect = text.get_rect(center=(pos[0], pos[1] - 15))
        # Add a small black background for better coordinate visibility
        bg_rect = text_rect.copy()
        bg_rect.inflate_ip(10, 6)
        pygame.draw.rect(screen, BLACK, bg_rect)
        screen.blit(text, text_rect)

def main():
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        draw_graph()
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS
    
    pygame.quit()

if __name__ == "__main__":
    main()

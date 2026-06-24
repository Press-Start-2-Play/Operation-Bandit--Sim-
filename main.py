from config import height, width, SPACING
import time, random, math, pygame
from grid import Grid

# Initialization 
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
pygame.display.set_caption('Operation Bandit Sim')

#Main Loop
running = True 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    Grid.grid_display(screen, width, height, SPACING)

    pygame.display.flip()
    clock.tick(60)

    



from config import height, width, SPACING, center
import time, random, math, pygame
from grid import Grid
from drones import Drone

# Initialization 
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
Drone_1  = Drone(center)
pygame.display.set_caption('Operation Bandit Sim')

#Main Loop
running = True 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    Grid.grid_display(screen, width, height, SPACING)
    Drone_1.centre_movement(0.016)
    pygame.draw.circle(screen, (0, 255, 0), Drone_1.position, 3 )

    pygame.display.flip()
    clock.tick(60)

    



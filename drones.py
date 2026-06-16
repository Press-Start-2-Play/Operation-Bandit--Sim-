import pygame
import time
import math 

class Drone:
    def __init__(self, center):
        self.origin = center
        self.position = pygame.Vector2(1000, 700) #Each drone starts outside the grid.
        self.velocity = pygame.Vector2(0,0)
        self.max_speed = 100 #px/s
        self.radius = 5
        self.color = (0, 255, 0)
        self.fov_base = 30
        self.fov_radius = self.fov_base
        self.fov_max = ((center.x**2 + center.y**2)**0.5) / 2 # Max distance from the center to a corner of the grid (diagonal from center)

    
        

    
    
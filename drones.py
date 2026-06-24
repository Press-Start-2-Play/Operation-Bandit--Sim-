import pygame
from grid import Grid
import random
import time
import math 

class Drone:
    total_drones = 0
    drones = []
    droneStartingPositions = [(450, -50), (900, 400), (450, 750), (-50, 400)] # Starting positions for drones (outside the grid)
    def __init__(self, center):
        self.origin = center
        self.heading = pygame.Vector2(0, 0)
        self.position = pygame.Vector2((random.choice(self.droneStartingPositions))) - center #Each drone starts outside the grid.
        self.speed_across= 100
        self.speed_inspect =  30
        self.velocity = self.heading * self.speed_across
        self.radius = 5
        self.color = (0, 255, 0)
        self.fov_base = 30
        self.fov_radius = self.fov_base
        self.fov_max = ((center.x**2 + center.y**2)**0.5) / 2 # Max distance from the center to a corner of the grid (diagonal from center)
        Drone.total_drones +=1
        Drone.drones.append(self)
    
    def radial_dispersal(cls):
        min_angle = int(360/ (Drone.total_drones))
        for i in range(1, Drone.total_drones+1):
            Drone.drones[i-1].heading = pygame.Vector2(math.cos(math.radians(min_angle * i)), math.sin(min_angle * i))
            print(min_angle * i)
            print(f"Drone {i} heading: {Drone.drones[i-1].heading}")

    def centre_movement(self, dt):
        direction_to_origin = (self.origin - self.position).normalize()
        self.heading = direction_to_origin
        self.velocity = self.heading * self.speed_across
        self.position += self.velocity * dt

    def move_across(self, dt):
        self.position += self.velocity * dt
    
    def update_map():
        pass

Drone_1  = Drone(pygame.Vector2(500, 450))
Drone_2  = Drone(pygame.Vector2(500, 450))
Drone_3  = Drone(pygame.Vector2(500, 450))
Drone_4  = Drone(pygame.Vector2(500, 450))
Drone.radial_dispersal(Drone)


    
    
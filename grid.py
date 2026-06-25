import pygame
class Grid:
    def __init__(self, screen, width, height, SPACING):
        self.screen = screen
        self.width = width
        self.height = height
        self.SPACING = SPACING

    def grid_display(screen, width, height,SPACING):
        screen.fill((0, 0, 0))
        for x in range(0, width, SPACING):
            pygame.draw.aaline(screen, (255, 255, 255), (x, 0), (x, height), 1)
        for y in range(0, height, SPACING):
            pygame.draw.line(screen, (255, 255, 255), (0, y), (width, y), 1)
        pygame.draw.circle(screen, (200, 0, 0), (width // 2, height // 2), 1.5)
    

# I'd be making the spacing like 15. Tht screen would be 700 by 900... I think that's okay.

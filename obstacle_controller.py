from obstacle_detection_function import get_obstacles, get_surface
import pygame  # could be moved to only required functions


class Obstacle_Controller:
    def __init__(self, camera, screen):
        self.camera = camera
        surface = get_surface(get_obstacles(self.camera))
        self.surface = surface
        mask_alpha = surface.convert_alpha()
        self.obstacle_mask = pygame.mask.from_surface(mask_alpha)
        self.screen = screen
        self.last_called = 0

    def handleTick(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_called > 1000:
            self.update_obstacles()
            self.last_called = current_time

    def update_obstacles(self):
        """ Updates the obstacle mask based on the camera """
        surface = get_surface(get_obstacles(self.camera))
        self.surface = surface
        mask_alpha = surface.convert_alpha()
        self.obstacle_mask = pygame.mask.from_surface(mask_alpha)

    def get_obstacles_mask(self):
        """ Returns the obstacle mask as a pygame mask """
        return self.obstacle_mask


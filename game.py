import pygame
import numpy as np
import cv2
import math
from time import sleep

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True

# Load image
file = "obstacle_mask.png"
loaded_mask = cv2.imread(file, cv2.IMREAD_COLOR)

# Convert to RGBA and set alpha
loaded_mask_rgba = cv2.cvtColor(loaded_mask, cv2.COLOR_BGR2RGBA)
loaded_mask_rgba[:, :, 3] = np.where(
    (loaded_mask_rgba[:, :, 0:3] == [0,0,0]).all(axis=2),
    0,  # Transparent
    255  # Opaque
)

alpha_channel = np.where(
    (loaded_mask_rgba[:, :, 0:3] == [0, 0, 0]).all(axis=2),
    0,  # Transparent
    255  # Opaque
)
# Binary obstacle mask
obstacle_mask = alpha_channel > 0


# Create Pygame surface
height, width = loaded_mask.shape[:2]
mask_surface = pygame.image.frombuffer(
    loaded_mask_rgba.tobytes(),
    (width, height),
    'RGBA'
).convert_alpha()

player = {
    "x": 960,
    "y": 540,
    "rotation": 0,
    "width": 60,
    "height": 90
    }


def cast_rays(player, max_distance=700):
    start_angle = player["rotation"]
    start_x = player["x"]
    start_y = player["y"]

    for i in range(-5,5):
        start_x = player["x"] + math.cos(start_angle) * i * 6
        start_y = player["y"] - math.sin(start_angle) * i * 6

        for pixel in range(max_distance):
            target_x = int(start_x + math.sin(start_angle) * pixel)
            target_y = int(start_y + math.cos(start_angle) * pixel)
            if 0 <= target_x < alpha_channel.shape[1] and 0 <= target_y < alpha_channel.shape[0]:
                if alpha_channel[target_y][target_x] > 0:
                    print(alpha_channel[target_y][target_x])
                    print("found")
                    print(target_x)
                    print(target_y)
                    break

        pygame.draw.line(screen, (255, 50, 50), (start_x, start_y), (target_x, target_y))


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("purple")
    screen.blit(mask_surface, (0, 0))
    # Draw player
    # Create base player surface
    player_surface = pygame.Surface((player["width"], player["height"]), pygame.SRCALPHA)
    pygame.draw.rect(player_surface, "blue", player_surface.get_rect())

# Rotate the surface around its center
    rotated_surface = pygame.transform.rotate(player_surface, math.degrees(player["rotation"]))
    rotated_rect = rotated_surface.get_rect(center=(player["x"], player["y"]))

# Draw the rotated player
    screen.blit(rotated_surface, rotated_rect.topleft)
    cast_rays(player, max_distance=500)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player["rotation"] = player["rotation"] - 0.01
    elif keys[pygame.K_RIGHT]:
        player["rotation"] = player["rotation"] + 0.01
#    elif keys[pygame.K_UP]:
#    elif keys[pygame.K_DOWN]:

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

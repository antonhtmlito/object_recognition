import pygame
import numpy as np
import cv2
import math

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
alpha_channel = np.where(
    (loaded_mask_rgba[:, :, 0:3] == [0, 0, 0]).all(axis=2),
    0,  # Transparent
    255  # Opaque
)
loaded_mask_rgba[:, :, 3] = alpha_channel

# Create Pygame surface
height, width = loaded_mask.shape[:2]
mask_surface = pygame.image.frombuffer(
    loaded_mask_rgba.tobytes(),
    (width, height),
    'RGBA'
).convert_alpha()

# Binary obstacle mask
obstacle_mask = alpha_channel > 0

# Player setup
player = {
    "x": 960,
    "y": 540,
    "rotation": 0,  # Degrees
    "width": 60,
    "height": 90,
    "speed": 4,
    "rotation_speed": 3  # Degrees/frame
}

def cast_rotated_ray(player, obstacle_mask, max_distance=700):
    rad = math.radians(player["rotation"])
    # Start at head (top center of player)
    start_x = player["x"]
    start_y = player["y"] - player["height"] // 2

    for i in range(max_distance):
        ray_x = int(start_x + math.cos(rad) * i)
        ray_y = int(start_y + math.sin(rad) * i)

        if 0 <= ray_x < obstacle_mask.shape[1] and 0 <= ray_y < obstacle_mask.shape[0]:
            if obstacle_mask[ray_y, ray_x]:
                return (ray_x, ray_y), i
        else:
            break
    return (ray_x, ray_y), None  # If it didn't hit anything

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    # Rotation
    if keys[pygame.K_a]:
        player["rotation"] -= player["rotation_speed"]
    if keys[pygame.K_d]:
        player["rotation"] += player["rotation_speed"]

    # Movement (forward/backward)
    rad = math.radians(player["rotation"])
    dx = math.cos(rad) * player["speed"]
    dy = math.sin(rad) * player["speed"]

    if keys[pygame.K_w]:
        player["x"] += dx
        player["y"] += dy
    if keys[pygame.K_s]:
        player["x"] -= dx
        player["y"] -= dy

    # Drawing
    screen.fill("purple")
    screen.blit(mask_surface, (0, 0))

# Create a surface for the player rectangle
    player_surface = pygame.Surface((player["width"], player["height"]), pygame.SRCALPHA)
    pygame.draw.rect(player_surface, "blue", (0, 0, player["width"], player["height"]))

# Rotate the surface around its center
    rotated_surface = pygame.transform.rotate(player_surface, -player["rotation"])  # Negative due to Pygame's coordinate system
    rotated_rect = rotated_surface.get_rect(center=(player["x"], player["y"]))

# Draw rotated player
    screen.blit(rotated_surface, rotated_rect.topleft)

# Raycasting
    (ray_end_x, ray_end_y), distance = cast_rotated_ray(player, obstacle_mask)
    ray_start = (int(player["x"]), int(player["y"] - player["height"] // 2))
    pygame.draw.line(screen, "red", ray_start, (ray_end_x, ray_end_y), 2)

# Optional: show distance
    if distance is not None:
        font = pygame.font.SysFont(None, 30)
        text = font.render(f"Distance: {distance}px", True, (255, 255, 255))
        screen.blit(text, (10, 10))

    # Raycasting
    (ray_end_x, ray_end_y), distance = cast_rotated_ray(player, obstacle_mask)
    ray_start = (int(player["x"]), int(player["y"] - player["height"] // 2))
    pygame.draw.line(screen, "red", ray_start, (ray_end_x, ray_end_y), 2)

    # Optional: show distance text
    if distance is not None:
        font = pygame.font.SysFont(None, 30)
        text = font.render(f"Distance: {distance}px", True, (255, 255, 255))
        screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

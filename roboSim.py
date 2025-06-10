import time
import pygame
import numpy as np
import cv2
import math
from robodetectíon import getBotPosition
from detect_white_and_yellow_ball import get_ball_positions
from roboController import RoboController
import routing_functions
import routing_manager

SIMULATION_MODE = False

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

# Global variables predefined
player = {
    "x": 300,
    "y": 300,
    "rotation": 0,
    "width": 30,
    "height": 50,
    }
obstacle = {
    "x": 0,
    "y": 0,
}
targets = {
    "list": []
}

roboController = RoboController()


def cast_rays(player, max_distance=700):
    start_angle = player["rotation"]

    for i in range(-5, 5):
        offset_angle = start_angle + (i * 0.05)
        ray_start_x = player["x"]
        ray_start_y = player["y"]

        for pixel in range(max_distance):
            target_x = int(ray_start_x + math.cos(offset_angle) * pixel)
            target_y = int(ray_start_y + math.sin(offset_angle) * pixel)
            if 0 <= target_x < alpha_channel.shape[1] and 0 <= target_y < alpha_channel.shape[0]:
                if alpha_channel[target_y][target_x] > 0:
                    break

        pygame.draw.line(screen, (255, 50, 50), (ray_start_x, ray_start_y), (target_x, target_y))


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("camera not openened")

routing_functions.init_targets()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            routing_functions.all_targets.append((mouse_x, mouse_y))
            routing_functions.calculate_target()
        if event.type == pygame.K_UP:
            running = False
            print("forward")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                routing_functions.init_targets()
                print("targets: ", len(routing_functions.all_targets))

    if SIMULATION_MODE:
        routing_manager.handle_simulated_routing(player, obstacle)
        tx, ty = routing_functions.target_x, routing_functions.target_y
        # Wall avoidance
        tx, ty = routing_functions.avoid_walls(tx, ty)
        routing_functions.target_x = tx
        routing_functions.target_y = ty
        ball_positions = {}
    else:
        botPos = getBotPosition(cap)
        if botPos is not None:
            player["x"] = botPos["position"][0]
            player["y"] = botPos["position"][1]
            player["rotation"] = botPos["angle"]
        ball_positions = get_ball_positions(cap)
        routing_manager.handle_routing(player, obstacle, roboController)

    # Add each detected ball position as a target (if it isn’t already in the list)
    for coords in ball_positions.values():
        for (bx, by) in coords:
            if (bx, by) not in routing_functions.all_targets:
                routing_functions.all_targets.append((bx, by))

    screen.fill("black")

    # Draw a cross obstacle in the center of the screen
    center_x, center_y = 400, 400
    pygame.draw.line(screen, "white", (center_x - 50, center_y), (center_x + 50, center_y), 5)
    pygame.draw.line(screen, "white", (center_x, center_y - 50), (center_x, center_y + 50), 5)

    # Set simulated obstacle coordinates for routing
    obstacle["x"] = center_x
    obstacle["y"] = center_y

    screen.blit(mask_surface, (0, 0))

    # Now draw each ball as before
    for color_name, coords in ball_positions.items():
        if "white" in color_name.lower():
            py_color = (255, 255, 255)
        elif "orange" in color_name.lower():
            py_color = (0, 140, 255)
        else:
            py_color = (200, 200, 200)

        # Removed duplicate ball drawing here

    # Draw player
    # Create base player surface
    player_surface = pygame.Surface((player["width"], player["height"]), pygame.SRCALPHA)
    pygame.draw.rect(player_surface, "blue", player_surface.get_rect())

# Draw targets
    for tx, ty in routing_functions.all_targets:
        pygame.draw.circle(screen, "red", (tx, ty), 8)

# handle routing
#    routing_manager.handle_routing(player, obstacle, roboController)

# Rotate the surface around its center
    rotated_surface = pygame.transform.rotate(player_surface, -math.degrees(player["rotation"]))
    print("rotation:", math.degrees(player["rotation"] + math.pi))
    rotated_rect = rotated_surface.get_rect(center=(player["x"], player["y"]))

# Draw the rotated player
    screen.blit(rotated_surface, rotated_rect.topleft)
    cast_rays(player, max_distance=10)

    # Draw walls (600x600 boundary)
    pygame.draw.line(screen, (255, 255, 255), (0, 0), (600, 0), 2)       # Top
    pygame.draw.line(screen, (255, 255, 255), (0, 0), (0, 600), 2)       # Left
    pygame.draw.line(screen, (255, 255, 255), (600, 0), (600, 600), 2)   # Right
    pygame.draw.line(screen, (255, 255, 255), (0, 600), (600, 600), 2)   # Bottom

    pygame.display.flip()
    clock.tick(20)

pygame.quit()
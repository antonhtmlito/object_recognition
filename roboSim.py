import time
import os

from robodetectíon import getBotPosition

import pygame
import numpy as np
import cv2
import math
from robodetectíon import getBotPosition
from detect_white_and_yellow_ball import get_ball_positions
from roboController import RoboController
import routing_functions
from calibration import load_color_mapping

# Load color mapping
script_dir = os.path.dirname(os.path.abspath(__file__))
color_file = os.path.join(script_dir, "colors.json")
colour_mapping = load_color_mapping(color_file)

if colour_mapping:
    for obj in colour_mapping:
        if obj.get("name") == "obstacle":
            obstacle_color = obj
            print(f"Obstacle color: {obstacle_color}")
            break

if obstacle_color is None:
    print("Error: Obstacle color not found in color mapping")
    exit(1)

lower_bound = np.array(obstacle_color["colorLowerBound"])
upper_bound = np.array(obstacle_color["colorUpperBound"])

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True

# Update interval
last_update_time = time.time()
update_interval = 0.1  # seconds

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
    "x": 0,
    "y": 0,
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
    start_angle = player["rotation"] - (math.pi / 2)
    start_x = player["x"]
    start_y = player["y"]

    for i in range(-5, 5):
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


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("camera not openened")


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

    botPos = getBotPosition(cap)
#    print(botPos)
    if botPos is not None:
        player["x"] = botPos["position"][0]
        player["y"] = botPos["position"][1]
        player["rotation"] = botPos["angle"]

    ball_positions = get_ball_positions(cap)

    screen.fill("black")
    screen.blit(mask_surface, (0, 0))

    for color_name, coords in ball_positions.items():
        # decide Pygame color by inspecting the HSV‐based name
        if "white" in color_name.lower():
            py_color = (255, 255, 255)
        elif "orange" in color_name.lower():
            py_color = (0, 140, 255)
        else:
            py_color = (200, 200, 200)

        for (bx, by) in coords:
            pygame.draw.circle(screen, py_color, (bx, by), 8)
    # Draw player
    # Create base player surface
    player_surface = pygame.Surface((player["width"], player["height"]), pygame.SRCALPHA)
    pygame.draw.rect(player_surface, "blue", player_surface.get_rect())

# Update data
    current_time = time.time()
    if current_time - last_update_time > update_interval:
        routing_functions.update_robot_state(player)
        routing_functions.update_obstacle_state(obstacle)
        # update_targets_state(targets)
        last_update_time = current_time

# Draw targets
    for tx, ty in routing_functions.all_targets:
        pygame.draw.circle(screen, "red", (tx, ty), 8)

# Remove targets
    if routing_functions.target_x is not None and routing_functions.target_y is not None:
        if abs(routing_functions.robot_x - routing_functions.target_x) < 50 and abs(routing_functions.robot_y - routing_functions.target_y) < 50:
            if (routing_functions.target_x, routing_functions.target_y) in routing_functions.all_targets:
                routing_functions.all_targets.remove((routing_functions.target_x, routing_functions.target_y))
            routing_functions.calculate_target()

# Drive to target
    angle_to_turn = routing_functions.calculate_angle(routing_functions.target_x, routing_functions.target_y)
    #print("angle to turn: ", angle_to_turn)
    print("targets:", routing_functions.target_x, routing_functions.target_y)
    if angle_to_turn is None:
        pass
    elif angle_to_turn > 5:
        roboController.rotate_clockwise(angle_to_turn)
        time.sleep(0.05)
    elif angle_to_turn < -5:
        roboController.rotate_counterClockwise(abs(angle_to_turn))
        time.sleep(0.05)
    else:
        distance = routing_functions.calculate_distance(routing_functions.target_x, routing_functions.target_y)
        if distance > 5:
            roboController.forward(0.5)
            time.sleep(0.05)

# Rotate the surface around its center
    rotated_surface = pygame.transform.rotate(player_surface, (math.degrees(player["rotation"] + math.pi) - 90) % 360 )
    print("rotation:", math.degrees(player["rotation"] + math.pi))
    rotated_rect = rotated_surface.get_rect(center=(player["x"], player["y"]))

# Draw the rotated player
    screen.blit(rotated_surface, rotated_rect.topleft)
    cast_rays(player, max_distance=500)

    keys = pygame.key.get_pressed()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()


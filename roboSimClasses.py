import time
from obstacle_detection_function import get_obstacles, get_surface

import pygame
import numpy as np
import cv2
import math
from robodetectíon import getBotPosition
from detect_white_and_yellow_ball import get_ball_positions
from roboController import RoboController
import routing_functions
from target_tracking import update_target_candidates
from ray_functions import cast_rays, cast_ray_at_angle
import route_goal
from routingController import RoutingController
from ballController import BallController
from obstacle_controller import Obstacle_Controller

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True

# Update interval
last_update_time = time.time()
update_interval = 1  # seconds

# Global variables predefined
player = {
    "x": 0,
    "y": 0,
    "rotation": 0,
    "width": 30,
    "height": 50,
    }

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("camera not openened")

roboController = RoboController()

ballController = BallController(
        camera=cap,
        )

obstacleController = Obstacle_Controller(
        camera=cap,
        screen=screen
        )

routingController = RoutingController(
        robot=player,
        roboController=roboController,
        ballController=ballController,
        obstacle_controller=obstacleController,
        screen=screen
        )

while running:
    # pygame settings
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            routing_functions.all_targets.append((mouse_x, mouse_y))
            routing_functions.calculate_target()

    botPos = getBotPosition(cap)
    if botPos is not None:
        player["x"] = botPos["position"][0]
        player["y"] = botPos["position"][1]
        player["rotation"] = botPos["angle"]

    ball_positions = get_ball_positions(cap)

    screen.fill("black")

    # Draw player
    player_surface = pygame.Surface((player["width"], player["height"]), pygame.SRCALPHA)
    pygame.draw.rect(player_surface, "blue", player_surface.get_rect())

# Update data
    current_time = time.time()
    if current_time - last_update_time > update_interval:
        # run this every second
        obstacleController.update_obstacles()
        ballController.handleTick()
        routingController.handleTick(time=1) # TODO: Proper time
        last_update_time = current_time


# Rotate the robot around its center
    rotated_surface = pygame.transform.rotate(player_surface, (math.degrees(player["rotation"] + math.pi) - 90) % 360 )
    rotated_surface = pygame.transform.flip(rotated_surface, False, True)
    rotated_rect = rotated_surface.get_rect(center=(player["x"], player["y"]))

    for target in ballController.targets:
        print(target)
        pygame.draw.circle(screen, "red", (target.x, target.y), 5)

# Draw the rotated player
    screen.blit(obstacleController.surface, (0, 0))
    screen.blit(rotated_surface, rotated_rect.topleft)

    keys = pygame.key.get_pressed()

    pygame.display.flip()
    clock.tick(20)

pygame.quit()

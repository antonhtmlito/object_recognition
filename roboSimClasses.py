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
    "width": 100,
    "height": 120,
    }

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("camera not openened")


roboController = RoboController()

ballController = BallController(
        camera=cap,
        screen=screen,
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
        screen=screen,
        camera=cap
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

    # Update data
    current_time = time.time()
    if current_time - last_update_time > update_interval:
        # run this every second
        ...  # Should be handled in each class
    obstacleController.handleTick()
    ballController.handleTick()
    routingController.handleTick()
    last_update_time = current_time

    # Draw player
    player_surface = pygame.Surface((player["width"], player["height"]), pygame.SRCALPHA)
    pygame.draw.rect(player_surface, "blue", player_surface.get_rect())

    # Draw current target
    if routingController.currentTarget is not None:
        x, y = routingController.currentTarget.position
        if routingController.currentTarget.targetType == "goal":
            pygame.draw.circle(screen, "blue", (x, y), 10)
        if routingController.currentTarget.targetType == "whiteBall":
            pygame.draw.circle(screen, "yellow", (x, y), 10)
        if routingController.currentTarget.targetType == "orangeBall":
            pygame.draw.circle(screen, "orange", (x, y), 10)
        if routingController.currentTarget.targetType == "checkpoint":
            pygame.draw.circle(screen, "purple", (x, y), 10)
        if routingController.currentTarget.targetType == "checkpointDetour":
            pygame.draw.circle(screen, "pink", (x, y), 10)

    # Rotate the robot around its center
    rotated_surface = pygame.transform.rotate(player_surface, (math.degrees(player["rotation"] + math.pi) - 90) % 360 )
    rotated_surface = pygame.transform.flip(rotated_surface, False, True)
    rotated_rect = rotated_surface.get_rect(center=(player["x"], player["y"]))

    for target in ballController.targets:
        pygame.draw.circle(screen, "red", (target.x, target.y), 5)

    # Draw the rotated player
    screen.blit(obstacleController.surface, (0, 0))
    screen.blit(rotated_surface, rotated_rect.topleft)

    keys = pygame.key.get_pressed()

    font = pygame.font.Font(None, 36)
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    screen.blit(fps_t,(0,0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

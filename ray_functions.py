import math
import pygame


def cast_rays(player, max_distance=700, screen=None, mask=None, num_rays=90):
    origin = (int(player["x"]), int(player["y"]))
    start_angle = player["rotation"] - math.pi / 2  # Adjust for image orientation
    angle_step = math.pi / num_rays  # Full cone: 180 degrees in radians

    for i in range(num_rays + 1):
        angle = start_angle + i * angle_step

        cast_ray_at_angle(player=player, screen=screen, angle=angle, max_distance=max_distance, mask=mask)


def cast_ray_at_angle(player, screen, angle, max_distance, mask):
    angle = math.radians(angle)
    dy = math.sin(angle)
    dx = math.cos(angle)
    origin = (int(player["x"]), int(player["y"]))

    for distance in range(0, max_distance, 1):  # step size 5 pixels
        target_x = int(origin[0] + dx * distance)
        target_y = int(origin[1] + dy * distance)

        if not (0 <= target_x < mask.get_size()[0] and 0 <= target_y < mask.get_size()[1]):
            break

        if mask.get_at((target_x, target_y)):
            pygame.draw.line(screen, (255, 50, 50), origin, (target_x, target_y))
            return (target_x, target_y)
    else:
        end_x = int(origin[0] + dx * max_distance)
        end_y = int(origin[1] + dy * max_distance)
        pygame.draw.line(screen, (100, 100, 100), origin, (end_x, end_y))
    return None

def cast_rays_from_target(target, max_distance=100, screen=None, mask=None):
    """ casts 4 rays from each target in each direction """
    directions = [0, 90, 180, 270]
    results = []

    for angle in directions:
        hit = cast_ray_at_angle(player=target, screen=screen, angle=angle, max_distance=max_distance, mask=mask)
        results.append(hit)
    return results

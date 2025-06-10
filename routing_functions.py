import math

robot_x = 0
robot_y = 0
robot_angle = 0
obstacle_x = 0
obstacle_y = 0
target_x = 300
target_y = 300
all_targets = []
detour_memory = set()
# Robot state
def update_robot_state(player):
    global robot_x, robot_y, robot_angle
    robot_x = player["x"]
    robot_y = player["y"]
    robot_angle = (player["rotation"])

# Obstacle state
def update_obstacle_state(obstacle):
    global obstacle_x, obstacle_y
    obstacle_x = obstacle["x"]
    obstacle_y = obstacle["y"]

# Target state
def update_targets_state(targets):
    global all_targets
    all_targets = targets

# Calculate closest target
def calculate_target():
    global target_x, target_y

    if not all_targets:
        target_x, target_y = None, None
        return target_x, target_y

    closest_target = None
    min_distance = float('inf')

    for tx, ty in all_targets:
        distance = calculate_distance(tx, ty)
        if distance < min_distance:
            min_distance = distance
            closest_target = (tx, ty)

    if closest_target:
        tx, ty = closest_target
    else:
        tx, ty = None, None

    target_x, target_y = tx, ty
    return target_x, target_y

# Check for whether the path is blocked
def is_path_blocked(target_x, target_y, threshold=60):
    distance_to_line = abs((target_y - robot_y) * obstacle_x - (target_x - robot_x) * obstacle_y + target_x * robot_y - target_y * robot_x) / math.hypot(target_x - robot_x, target_y - robot_y)
    return distance_to_line < threshold and min(robot_x, target_x) < obstacle_x < max(robot_x, target_x)

# Calculate simple detour point
def find_detour( detour_distance=100):
    obstacle_angle = math.atan2(obstacle_y - robot_y, obstacle_x - robot_x)
    detour_angle = obstacle_angle + math.radians(90)
    detour_x = obstacle_x + detour_distance * math.cos(detour_angle)
    detour_y = obstacle_y + detour_distance * math.sin(detour_angle)
    return detour_x, detour_y

# Angle from robot to target
def calculate_angle(target_x, target_y):
    if target_x is None or target_y is None:
        return None
    angle_to_target = math.degrees(math.atan2(target_y - robot_y, target_x - robot_x))
    angle_difference = (angle_to_target - math.degrees(robot_angle) + 360) % 360
    return angle_difference if angle_difference <= 180 else angle_difference - 360

# Distance from robot to target
def calculate_distance(target_x, target_y):
    distance_to_target = math.sqrt((target_x - robot_x) ** 2 + (target_y - robot_y) ** 2)
    return distance_to_target

# Avoid Walls
walls = [
    (0, 0, 0, 600),      # venstre
    (0, 0, 600, 0),      # øverste
    (600, 0, 600, 600),  # højre
    (0, 600, 600, 600)   # bund
]

def avoid_walls(target_x, target_y, wall_threshold=100, detour_distance=200):
    if target_x is None or target_y is None:
        return target_x, target_y
    if (target_x, target_y) in detour_memory:
        return target_x, target_y
    for x1, y1, x2, y2 in walls:
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2
        dist = abs(A * target_x + B * target_y + C) / math.hypot(A, B)
        if dist < wall_threshold:
            wall_dx = x2 - x1
            wall_dy = y2 - y1
            norm = math.hypot(wall_dx, wall_dy)
            if norm == 0:
                continue
            wall_dx /= norm
            wall_dy /= norm

            if robot_x - target_x <= 0: # right wall
                perp_dx = -wall_dy
            if robot_y - target_y <= 0:
                perp_dy = -wall_dx
            if robot_x - target_x >= 0:
                perp_dx = wall_dy
            if robot_y - target_y >= 0:
                perp_dy = wall_dx

            detour_x = target_x + perp_dx * detour_distance
            detour_y = target_y + perp_dy * detour_distance
            detour = (detour_x, detour_y)

            # Check if detour is already directly before target
            try:
                idx = all_targets.index((target_x, target_y))
                if idx == 0 or all_targets[idx - 1] != detour:
                    all_targets.insert(idx, detour)
                    detour_memory.add((target_x, target_y))
            except ValueError:
                pass
            break
    return target_x, target_y

def is_facing_wall(threshold_distance=100, facing_dot_threshold=0.7):
    for x1, y1, x2, y2 in walls:
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2
        dist_to_wall = abs(A * robot_x + B * robot_y + C) / math.hypot(A, B)
        if dist_to_wall < threshold_distance:
            wall_dx = x2 - x1
            wall_dy = y2 - y1
            norm = math.hypot(wall_dx, wall_dy)
            if norm == 0:
                continue
            wall_dx /= norm
            wall_dy /= norm
            perp_dx = -wall_dy
            perp_dy = wall_dx

            dot = math.cos(robot_angle) * perp_dx + math.sin(robot_angle) * perp_dy
            print("dot: ", dot)
            if dot > facing_dot_threshold:
                return True, (perp_dx, perp_dy)
    return False, (0, 0)

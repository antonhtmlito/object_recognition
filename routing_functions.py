import math

# Robot state
def update_robot_state(player):
    global robot_x, robot_y, robot_angle
    robot_x = player["x"]
    robot_y = player["y"]
    robot_angle = math.radians(player["rotation"])

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
    angle_difference = (angle_to_target - robot_angle + 360) % 360
    return angle_difference if angle_difference <= 180 else angle_difference - 360

# Distance from robot to target
def calculate_distance(target_x, target_y):
    distance_to_target = math.sqrt((target_x - robot_x) ** 2 + (target_y - robot_y) ** 2)
    return distance_to_target

import routing_functions
import time
import math

# Update interval
last_update_time = time.time()
update_interval = 0.1  # seconds

def handle_routing(player, obstacle, roboController):
    global last_update_time
# Update data
    current_time = time.time()
    if current_time - last_update_time > update_interval:
        routing_functions.update_robot_state(player)
        routing_functions.update_obstacle_state(obstacle)
        # update_targets_state(targets)
        last_update_time = current_time
        routing_functions.calculate_target()
        # Move detour logic here to execute immediately when real target is assigned
        tx, ty = routing_functions.target_x, routing_functions.target_y
        if tx is not None and ty is not None:
            routing_functions.target_x, routing_functions.target_y = routing_functions.avoid_walls(tx, ty)

# Remove targets
    if routing_functions.target_x is not None and routing_functions.target_y is not None:
        if abs(routing_functions.robot_x - routing_functions.target_x) < 50 and abs(routing_functions.robot_y - routing_functions.target_y) < 50:
            if (routing_functions.target_x, routing_functions.target_y) in routing_functions.all_targets:
                routing_functions.all_targets.remove((routing_functions.target_x, routing_functions.target_y))
            routing_functions.calculate_target()
            # Move detour logic here as well after target recalculation
            tx, ty = routing_functions.target_x, routing_functions.target_y
            if tx is not None and ty is not None:
                routing_functions.target_x, routing_functions.target_y = routing_functions.avoid_walls(tx, ty)

# Drive to target
    angle_to_turn = routing_functions.calculate_angle(routing_functions.target_x, routing_functions.target_y)
    # print("angle to turn: ", angle_to_turn)
    print("targets:", routing_functions.target_x, routing_functions.target_y)
    if angle_to_turn is None:
        pass
    elif angle_to_turn > 3:
        roboController.rotate_clockwise(angle_to_turn)
        time.sleep(0.05)
    elif angle_to_turn < -3:
        roboController.rotate_counterClockwise(abs(angle_to_turn))
        time.sleep(0.05)
    else:
        distance = routing_functions.calculate_distance(routing_functions.target_x, routing_functions.target_y)
        if distance > 5:
            roboController.forward(0.5)
            time.sleep(0.05)

def handle_simulated_routing(player, obstacle):
    global last_update_time

    current_time = time.time()
    if current_time - last_update_time > update_interval:
        routing_functions.update_robot_state(player)
        routing_functions.update_obstacle_state(obstacle)
        last_update_time = current_time
        routing_functions.calculate_target()
        # Move detour logic here to execute immediately when real target is assigned
        tx, ty = routing_functions.target_x, routing_functions.target_y
        if tx is not None and ty is not None:
            routing_functions.target_x, routing_functions.target_y = routing_functions.avoid_walls(tx, ty)

    tx, ty = routing_functions.target_x, routing_functions.target_y
    # Wall avoidance handled above

    if tx is not None and ty is not None:
        # Obstacle avoidance
        if routing_functions.is_path_blocked(tx, ty):
            tx, ty = routing_functions.find_detour()
            routing_functions.target_x = tx
            routing_functions.target_y = ty

        dx = tx - player["x"]
        dy = ty - player["y"]
        distance = math.hypot(dx, dy)

        if distance < 1:
            if (tx, ty) in routing_functions.all_targets:
                routing_functions.all_targets.remove((tx, ty))
            should_back_up, (perp_dx, perp_dy) = routing_functions.is_facing_wall()
            if should_back_up:
                player["x"] -= perp_dx * 50
                player["y"] -= perp_dy * 50
                if routing_functions.all_targets:
                    # Turn toward next target
                    tx, ty = routing_functions.target_x, routing_functions.target_y
                    angle = math.atan2(ty - player["y"], tx - player["x"])
                    player["rotation"] = angle
                else:
                    # Turn around
                    player["rotation"] += math.pi
            routing_functions.calculate_target()
            # Move detour logic here after target recalculation
            tx, ty = routing_functions.target_x, routing_functions.target_y
            if tx is not None and ty is not None:
                routing_functions.target_x, routing_functions.target_y = routing_functions.avoid_walls(tx, ty)
        else:
            angle_to_target = math.atan2(dy, dx)
            angle_diff = angle_to_target - player["rotation"]
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

            TURN_SPEED = 0.1
            MOVE_THRESHOLD = 0.1

            if abs(angle_diff) > MOVE_THRESHOLD:
                player["rotation"] += TURN_SPEED * (1 if angle_diff > 0 else -1)
                return
            player["x"] += math.cos(player["rotation"]) * 2
            player["y"] += math.sin(player["rotation"]) * 2
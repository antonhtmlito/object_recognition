import routing_functions
import time
import math

# Update interval
last_update_time = time.time()
last_obs_update_time = time.time()
update_interval = 0.5  # seconds

def handle_routing(player, obstacle, goal, roboController):
    global last_update_time, last_obs_update_time
    # Update data
    current_time = time.time()
    if current_time - last_update_time > update_interval:
        routing_functions.update_robot_state(player)
        routing_functions.update_obstacle_state(obstacle)
        routing_functions.update_goal_state(goal)
        # update_targets_state(targets)
        last_update_time = current_time
        routing_functions.calculate_target()
        tx, ty = routing_functions.target_x, routing_functions.target_y
        if tx is not None and ty is not None:
            routing_functions.target_x, routing_functions.target_y = routing_functions.avoid_walls(tx, ty)

# Remove targets
    if routing_functions.target_x is not None and routing_functions.target_y is not None:
        if abs(routing_functions.robot_x - routing_functions.target_x) < 20 and abs(routing_functions.robot_y - routing_functions.target_y) < 20:
            if (routing_functions.target_x, routing_functions.target_y) in routing_functions.all_targets:
                routing_functions.all_targets.remove((routing_functions.target_x, routing_functions.target_y))
            routing_functions.calculate_target()
            tx, ty = routing_functions.target_x, routing_functions.target_y
            if tx is not None and ty is not None:
                routing_functions.target_x, routing_functions.target_y = routing_functions.avoid_walls(tx, ty)

# Drive to target
    angle_to_turn = routing_functions.calculate_angle(routing_functions.target_x, routing_functions.target_y)
    # print("angle to turn: ", angle_to_turn)
    print("target:", routing_functions.target_x, routing_functions.target_y)
    if routing_functions.target_total > routing_functions.target_goal or len(routing_functions.all_targets) != 0:
        now_time = time.time()
        if now_time - last_obs_update_time > update_interval:
            routing_functions.target_total = len(routing_functions.all_targets)
            print("OBS: ", routing_functions.target_total, routing_functions.target_goal)
            last_obs_update_time = now_time

        if angle_to_turn is None:
            return None
        elif angle_to_turn > 3:
            roboController.rotate_clockwise(angle_to_turn)
            time.sleep(0.05)
            return None
        elif angle_to_turn < -3:
            roboController.rotate_counterClockwise(abs(angle_to_turn))
            time.sleep(0.05)
            return None
        else:
            distance = routing_functions.calculate_distance(routing_functions.target_x, routing_functions.target_y)
            if distance > 5:
                roboController.forward(0.5)
                time.sleep(0.05)
                return None
            return None
    else:
        # Insert target perpendicular to wall before goal
        if not routing_functions.all_targets:
            min_dist = float('inf')
            closest_wall = None
            for x1, y1, x2, y2 in routing_functions.walls:
                A = y2 - y1
                B = x1 - x2
                C = x2 * y1 - x1 * y2
                dist = abs(A * routing_functions.goal_x + B * routing_functions.goal_y + C) / math.hypot(A, B)
                if dist < min_dist:
                    min_dist = dist
                    closest_wall = (x1, y1, x2, y2)

            if closest_wall:
                x1, y1, x2, y2 = closest_wall
                wall_dx = x2 - x1
                wall_dy = y2 - y1
                norm = math.hypot(wall_dx, wall_dy)
                if norm != 0:
                    wall_dx /= norm
                    wall_dy /= norm
                    perp_dx = -wall_dy
                    perp_dy = wall_dx
                    detour_x = routing_functions.goal_x + perp_dx * 200
                    detour_y = routing_functions.goal_y + perp_dy * 200
                    routing_functions.all_targets.insert(0, (detour_x, detour_y))
                    routing_functions.calculate_target()
                    return None

        dx = routing_functions.goal_x - player["x"]
        dy = routing_functions.goal_y - player["y"]
        angle_to_goal = math.atan2(dy, dx)
        angle_diff = angle_to_goal - player["rotation"]
        angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
        print("angle_diff:", angle_diff)

        if angle_diff is None:
             pass
        elif angle_diff > 3:
            roboController.rotate_clockwise(angle_diff)
            time.sleep(0.5)
        elif angle_to_turn < -3:
            roboController.rotate_counterClockwise(abs(angle_diff))
            time.sleep(0.5)
            return None
        else:
            distance_to_goal = math.sqrt((routing_functions.goal_x - routing_functions.robot_x) ** 2 + (routing_functions.goal_y - routing_functions.robot_y) ** 2)
            if distance_to_goal > 5:
                roboController.forward(0.5)
                time.sleep(0.5)
        if abs(routing_functions.robot_x - routing_functions.goal_x) <= 5 and abs(
                routing_functions.robot_y - routing_functions.goal_y) <= 5:
            roboController.dropoff()
            roboController.dropoff()
            time.sleep(2)
            routing_functions.init_targets()
            return None
        else:
            return None

def handle_simulated_routing(player, obstacle):
    global last_update_time

    current_time = time.time()
    if current_time - last_update_time > update_interval:
        routing_functions.update_robot_state(player)
        routing_functions.update_obstacle_state(obstacle)
        last_update_time = current_time
        routing_functions.calculate_target()
        tx, ty = routing_functions.target_x, routing_functions.target_y
        if tx is not None and ty is not None:
            routing_functions.target_x, routing_functions.target_y = routing_functions.avoid_walls(tx, ty)

    tx, ty = routing_functions.target_x, routing_functions.target_y

    if tx is not None and ty is not None:
        # Obstacle avoidance
        if routing_functions.is_path_blocked(tx, ty):
            tx, ty = routing_functions.find_detour()
            routing_functions.target_x = tx
            routing_functions.target_y = ty

        dx = tx - player["x"]
        dy = ty - player["y"]
        distance = math.hypot(dx, dy)

        while routing_functions.target_total > routing_functions.target_goal:
            print("OBS: ", routing_functions.target_total, routing_functions.target_goal)
            routing_functions.target_total = len(routing_functions.all_targets)
            if distance < 1:
                if (tx, ty) in routing_functions.all_targets:
                    routing_functions.all_targets.remove((tx, ty))
                #    routing_functions.last_target_removal_time = time.time()
                #should_back_up, (perp_dx, perp_dy) = routing_functions.is_facing_wall()
                #time_diff = time.time() - routing_functions.last_target_removal_time
                #print("time diff:", time_diff)
                #print("should back up:", should_back_up)
                #if should_back_up and time_diff < 2:
                #    player["x"] -= perp_dx * 50
                #    player["y"] -= perp_dy * 50
                #    if routing_functions.all_targets:
                #        # Turn toward next target
                #        tx, ty = routing_functions.target_x, routing_functions.target_y
                #        angle = math.atan2(ty - player["y"], tx - player["x"])
                #        player["rotation"] = angle
                #    else:
                #        # Turn around
                #        player["rotation"] += math.pi
                routing_functions.calculate_target()
                tx, ty = routing_functions.target_x, routing_functions.target_y
                if tx is not None and ty is not None:
                    routing_functions.target_x, routing_functions.target_y = routing_functions.avoid_walls(tx, ty)
                    return None
                else:
                    return None
            else:
                angle_to_target = math.atan2(dy, dx)
                angle_diff = angle_to_target - player["rotation"]
                angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

                TURN_SPEED = 0.1
                MOVE_THRESHOLD = 0.1

                if abs(angle_diff) > MOVE_THRESHOLD:
                    player["rotation"] += TURN_SPEED * (1 if angle_diff > 0 else -1)
                    return None
                player["x"] += math.cos(player["rotation"]) * 2
                player["y"] += math.sin(player["rotation"]) * 2
                return None
        else:
            dx = routing_functions.goal_x - player["x"]
            dy = routing_functions.goal_y - player["y"]
            angle_to_goal = math.atan2(dy, dx)
            angle_diff = angle_to_goal - player["rotation"]
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            print("angle_diff:", angle_diff)
            TURN_SPEED = 0.1
            MOVE_THRESHOLD = 0.1

            if abs(angle_diff) > MOVE_THRESHOLD:
                player["rotation"] += TURN_SPEED * (1 if angle_to_goal > 0 else -1)
                return None
            player["x"] += math.cos(player["rotation"]) * 2
            player["y"] += math.sin(player["rotation"]) * 2
            if abs(routing_functions.robot_x - routing_functions.goal_x) <= 5 and abs(routing_functions.robot_y - routing_functions.goal_y) <= 5:
                time.sleep(2)
                routing_functions.init_targets()
            else:
                return None

    else:
        return None
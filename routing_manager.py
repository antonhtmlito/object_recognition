import routing_functions
import time

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

# Remove targets
    if routing_functions.target_x is not None and routing_functions.target_y is not None:
        if abs(routing_functions.robot_x - routing_functions.target_x) < 50 and abs(routing_functions.robot_y - routing_functions.target_y) < 50:
            if (routing_functions.target_x, routing_functions.target_y) in routing_functions.all_targets:
                routing_functions.all_targets.remove((routing_functions.target_x, routing_functions.target_y))
            routing_functions.calculate_target()

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
import robodetectíon
import routing_functions
from roboController import RoboController

roboController = RoboController()

def go_to_goal(cap):
    goalpos = robodetectíon.getGoalPosition(cap)
    if goalpos is not None:
        goal_x = goalpos["position"][0]
        goal_y = goalpos["position"][1]

    angle_to_turn = routing_functions.calculate_angle(goal_x, goal_y)
    distance = routing_functions.calculate_distance(goal_x, goal_y)
    if goal_x and goal_y:
        if abs(routing_functions.robot_x - goal_x) < 220 and abs(routing_functions.robot_y - goal_y) < 220:
            roboController.dropoff()
            return True
        else:
            routing_functions.drive(angle_to_turn, distance)
    return False
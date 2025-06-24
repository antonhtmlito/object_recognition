from dataclasses import dataclass

@dataclass
class Values:
    area_low:   int = 230
    area_high:  int = 270
    radius_low: int = 20
    robot_id:   int = 4
    goal_id:    int = 102


values = Values()


DEBUG_BALLS = False
DEBUG_ROUTING = True
DEBUG_ROBOT = False
DEBUG_ROBOT_CONTROLLER = True
DEBUG_GOAL = False


GOAL_OFFSET = 140

ROUTING_UPDATE_INTERVAL = 500  # milliseconds
OBSTACLE_UPDATE_INERVAL = 1000  # milliseconds
ROBOT_UPDATE_INTERVAL = 300  # milliseconds
BALL_UPDATE_INTERVAL = 100  # milliseconds

TARGET_DISTANCE_FOR_REMOVING_BALL = 70  # pixels

import math
from roboController import RoboController
from obstacle_controller import Obstacle_Controller
from ballController import BallController
from ray_functions import cast_ray_at_angle
import time


# targets are in the form (x,y) or [x,y]
# robot is in the form currently found in roboSim for player

class RoutingController:
    def __init__(self, robot,
                 roboController: RoboController,
                 obstacle_controller: Obstacle_Controller,
                 ballController: BallController,
                 screen
                 ):
        self.robot = robot
        self.state = "goToBall"
        self.currentTarget = None  # should be (x, y)
        self.roboController = roboController
        self.obstacle_controller = obstacle_controller
        self.ballController = ballController
        self.storedBalls = 0
        self.screen = screen
        self.degree = 0

    def handleTick(self, time):
        """ handles the actions for a given tick in the simulation
        We only want to do certain actions every now and then and we handle this with a timestamp"""
        if self.currentTarget is None:
            print("setting new target")
            self.setCurrentTarget()  #Leave empty to auto calculate best target

        if self.storedBalls >= 4:
            ...  # Drive to goal
        else:
            self.driveToCurrentTarget()

    def driveToCurrentTarget(self):
        """ makes the robot drive to the current target """
        angle = self.getAngleToCurrentTarget()
        if angle is None:
            return
        print("angle to rotate", angle)
        hit = self.checkCollisionsForAngle(angle=angle["angleTarget"]) # for now angle is not used as it is defined elsewhere
        if hit is not None:
            self.handle_detour(angle)
        angle = angle["angleToTurn"]
        if angle > -3 and angle < 3:
            self.roboController.forward(0.1)
        else:
            print("in else")
            if angle < 0:
                print("rotate counter")
                self.roboController.rotate_counterClockwise(angle)
            elif angle > 0:
                print("rotate")
                self.roboController.rotate_clockwise(angle)
            else:
                raise Exception("Angle to turn somehow zero though it did not drive")
        self.handleTargetCollision()

    def handle_detour(self, angle):
        if angle["angleToTurn"] > 45:
            self.roboController.forward(0.5)
        else:
            if angle["angleToTurn"] > 0:
                self.roboController.rotate_clockwise(45)
            else:
                self.roboController.rotate_counterClockwise(45)
            self.roboController.forward(0.5)

    def handleTargetCollision(self):
        """ Does checks for if a ball is colelcted or not and handles that """
        if self.getDistanceToCurrentTarget() < 50:
            self.ballController.delete_target_at(self.currentTarget)
            self.storedBalls += 1
            self.currentTarget = None
        else:
            ...

    def setRobot(self, robot):
        self.robot = robot

    def setCurrentTarget(self, target=None):
        if target is None:
            self.currentTarget = self.calculateTarget()
        else:
            self.currentTarget = target

    def calculateTarget(self):
        if self.ballController.targets == []:
            print("no targets")
            self.currentTarget = None

        smallest_dist = 999999
        best_target = None
        for target in self.ballController.targets:
            distance = math.dist(target, (self.robot["x"], self.robot["y"]))
            if distance is None:
                return None
            if smallest_dist > distance:
                best_target = target

        return best_target

    def getAngleToCurrentTarget(self):
        """ Finds the angle which to turn to get to the current Target"""
        if self.currentTarget is None:
            return None
        angle_to_target = math.degrees(math.atan2(self.currentTarget[1] - self.robot["y"], self.currentTarget[0] - self.robot["x"]))
        angle_difference = (angle_to_target - math.degrees(self.robot["rotation"]) + 360) % 360
        angle_difference = angle_difference if angle_difference <= 180 else angle_difference - 360
        angle_dict = {"angleTarget": angle_to_target, "angleToTurn": angle_difference}
        return angle_dict

    def getDistanceToCurrentTarget(self):
        if self.currentTarget is None:
            return None
        distance = math.dist(
                    (self.robot["x"], self.robot["y"]),
                    self.currentTarget
                    )
        return distance

    def checkCollisionsForAngle(self, angle):
        hit = cast_ray_at_angle(
                player=self.robot,
                angle=angle,
                max_distance=int(self.getDistanceToCurrentTarget()+2),
                mask=self.obstacle_controller.get_obstacles_mask(),
                screen=self.screen
                                )
        if hit is None:
            return None
        return hit

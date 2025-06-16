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
            print("driving to target", self.currentTarget)
            self.driveToCurrentTarget()


    def driveToCurrentTarget(self):
        """ makes the robot drive to the current target """
        angle = self.getAngleToCurrentTarget()
        print("angle: ", angle)
        if angle is None:
            return
        self.checkCollisionsForAngle(angle=angle)
        if angle > -3 or angle < 3:
            self.roboController.forward(0.1)
        else:
            if angle < 0:
                self.roboController.rotate_counterClockwise(math.radians(angle))
            elif angle > 0:
                self.roboController.rotate_clockwise(math.radians(angle))
            else:
                raise Exception("Angle to turn somehow zero though it did not drive")
        self.handleTargetCollision()

    def handleTargetCollision(self):
        """ Does checks for if a ball is colelcted or not and handles that """
        if self.getDistanceToCurrentTarget() < 50:
            self.ballController.delete_target_at(self.currentTarget)
            self.storedBalls += 1
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
            print("targets in target finding loop: ", target)
            distance = math.dist(target, (self.robot["x"], self.robot["y"]))
            if distance is None:
                return None
            if smallest_dist > distance:
                best_target = target

        print("best target ", best_target)
        return best_target

    def getAngleToCurrentTarget(self):
        """ Finds the angle which to turn to get to the current Target"""
        if self.currentTarget is None:
            return None
        angle_to_target = math.degrees(math.atan2(self.currentTarget[1] - self.robot["y"], self.currentTarget[0] - self.robot["x"]))
        self.degree = angle_to_target
        angle_difference = (angle_to_target - math.degrees(self.robot["rotation"]) + 360) % 360
        angle_difference = angle_difference
        return angle_difference if angle_difference <= 180 else angle_difference - 360

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
                angle=self.degree,
                max_distance=int(self.getDistanceToCurrentTarget()+2),
                mask=self.obstacle_controller.get_obstacles_mask(),
                screen=self.screen
                                )
        print("angle collisoin ", angle)
        time.sleep(2)  # Only here So I can debug TODO: remove later
        if hit is None:
            return None
        return hit

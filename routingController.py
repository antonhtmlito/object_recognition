import math
from roboController import RoboController


# targets are in the form (x,y) or [x,y]
# robot is in the form currently found in roboSim for player

class RoutingController:
    def __init__(self, robot, roboController: RoboController, targets=[]):
        self.robot = robot
        self.targets = targets
        self.state = "goToBall"
        self.currentTarget = targets.get(0)
        self.roboController = roboController

    def driveToCurrentTarget(self):
        angle = self.getAngleToCurrentTarget()
        if angle > -3 or angle < 3:
            self.roboController.forward(0.1)
        else:
            if angle < 0:
                self.roboController.rotate_counterClockwise(math.radians(angle))
            elif angle > 0:
                self.roboController.rotate_clockwise(math.radians(angle))
            else:
                raise Exception("Angle to turn somehow zero though it did not drive")

    def handleTargetCollision(self):
        if self.getDistanceToCurrentTarget() < 50:
            ...  # remove ball
        else:
            ...

    def setRobot(self, robot):
        self.robot = robot

    def setTargets(self, targets):
        self.targets = targets

    def setCurrentTarget(self, target):
        self.currentTarget = target

    def calculateTarget(self):
        if self.targets == []:
            self.currentTarget = None

        smallest_dist = 999999
        best_target = None
        for target in self.targets:
            distance = self.getDistanceToCurrentTarget()
            if smallest_dist > distance:
                best_target = target

        return best_target

    def getAngleToCurrentTarget(self):
        if self.currentTarget is None:
            return None
        angle_to_target = math.degrees(math.atan2(target[1] - self.robot["y"], target[0], self.robot["x"]))
        angle_difference = (angle_to_target - math.degrees(self.robot["rotation"]) + 360) % 360
        return angle_difference if angle_difference <= 180 else angle_difference - 360

    def getDistanceToCurrentTarget(self):
        distance = math.dist(
                    (self.player["x"], self.player["y"]),
                    self.currentTarget
                    )
        return distance

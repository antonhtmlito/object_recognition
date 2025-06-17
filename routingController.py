import math
from roboController import RoboController
from obstacle_controller import Obstacle_Controller
from ballController import BallController
from ray_functions import cast_ray_at_angle
import time
import Target
import robodetectíon

# targets are in the form (x,y) or [x,y]
# robot is in the form currently found in roboSim for player

class RoutingController:
    def __init__(self, robot,
                 roboController: RoboController,
                 obstacle_controller: Obstacle_Controller,
                 ballController: BallController,
                 screen,
                 camera
                 ):
        self.robot = robot
        self.state = "goToBall"
        self.currentTarget = None  # should be a Target object
        self.roboController = roboController
        self.obstacle_controller = obstacle_controller
        self.ballController = ballController
        self.storedBalls = 0
        self.screen = screen
        self.camera = camera
        
    def handleTick(self, time):
        """ handles the actions for a given tick in the simulation
        We only want to do certain actions every now and then and we handle this with a timestamp"""
        if self.currentTarget is None:
            print("setting new target")
            self.setCurrentTarget()  #Leave empty to auto calculate best target

        if self.storedBalls >= 4:
            goalpos = robodetectíon.getGoalPosition(self.camera)
            if goalpos is not None:
                goal_x = goalpos["position"][0]
                goal_y = goalpos["position"][1]
            target = Target(targetType="goal", x=goal_x, y=goal_y)
            if self.currentTarget != target:
                self.setCurrentTarget(target)
            self.driveToCurrentTarget()
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
        if -3 < angle < 3:
            if self.currentTarget.approach_angle is not None:
                angle_rad = math.radians(self.currentTarget.approach_angle)
                checkpoint_x = self.currentTarget.x - 100 * math.cos(angle_rad)
                checkpoint_y = self.currentTarget.y - 100 * math.sin(angle_rad)
                checkpoint = (checkpoint_x, checkpoint_y)

                distance_to_checkpoint = math.dist((self.robot["x"], self.robot["y"]), checkpoint)

                if distance_to_checkpoint > 5:
                    checkpoint_angle = math.degrees(math.atan2(
                        checkpoint[1] - self.robot["y"],
                        checkpoint[0] - self.robot["x"]))
                    angle_diff = (checkpoint_angle - math.degrees(self.robot["rotation"]) + 360) % 360
                    angle_diff = angle_diff if angle_diff <= 180 else angle_diff - 360

                    if -3 < angle_diff < 3:
                        self.roboController.forward(0.1)
                    elif angle_diff < 0:
                        self.roboController.rotate_counterClockwise(abs(angle_diff))
                    else:
                        self.roboController.rotate_clockwise(angle_diff)
                    return
            self.roboController.forward(0.3)
        else:
            print("in else")
            if angle < 0:
                print("rotate counter")
                self.roboController.rotate_counterClockwise(abs(angle))
            elif angle > 0:
                print("rotate")
                self.roboController.rotate_clockwise(abs(angle))
            else:
                raise Exception("Angle to turn somehow zero though it did not drive")
        self.handleTargetCollision()

    def handle_detour(self, angle):
        ...
        

    def handleTargetCollision(self):
        """ Does checks for if a ball is colelcted or not and handles that """
        if self.getDistanceToCurrentTarget() < 30:
            self.ballController.delete_target_at(self.currentTarget)
            if self.currentTarget.targetType == "whiteBall":
                print("collected white ball")
                self.storedBalls += 1
            if self.currentTarget.targetType == "orangeBall":
                print("collected orange ball")
                self.storedBalls += 1
            if self.currentTarget.targetType == "checkpoint":
                print("reached checkpoint")
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
            distance = math.dist(target.position, (self.robot["x"], self.robot["y"]))
            if distance is None:
                return None
            if smallest_dist > distance:
                best_target = target

        return best_target

    def getAngleToCurrentTarget(self):
        """ Finds the angle which to turn to get to the current Target"""
        if self.currentTarget is None:
            return None
        angle_to_target = math.degrees(math.atan2(
            self.currentTarget.position[1] - self.robot["y"],
            self.currentTarget.position[0] - self.robot["x"]))
        angle_difference = (angle_to_target - math.degrees(self.robot["rotation"]) + 360) % 360
        angle_difference = angle_difference if angle_difference <= 180 else angle_difference - 360
        angle_dict = {"angleTarget": angle_to_target, "angleToTurn": angle_difference}
        return angle_dict

    def getDistanceToCurrentTarget(self):
        if self.currentTarget is None:
            return None
        distance = math.dist(
                    (self.robot["x"], self.robot["y"]),
                    self.currentTarget.position
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

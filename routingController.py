import math
from roboController import RoboController
from obstacle_controller import Obstacle_Controller
from ballController import BallController
from ray_functions import cast_ray_at_angle
from Target import Target
import time
from Target import Target
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
            self.handle_detour(angle, hit)
        angle = angle["angleToTurn"]
        if angle > -3 and angle < 3:
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

    def handle_detour(self, angle, hitPosition):
        """ Creates a checkpoint for the robot to get a better angle for the target """
        max_y = 1080
        max_x = 1920
        # Pick direction
        hit_x = hitPosition[0]
        hit_y = hitPosition[1]

        if hit_x > max_x / 2:
            x_direction = 1  # right
        else:
            x_direction = -1
        if hit_y > max_y / 2:
            y_direction = 1
        else:
            y_direction = -1

        # offset from the hit position

        offset_x = 100 * x_direction
        offset_y = 100 * y_direction

        new_target_x = hit_x + offset_x
        new_target_y = hit_y + offset_y

        # Create a new target
        new_target = Target(targetType="checkpoint", x=new_target_x, y=new_target_y)
        self.currentTarget = new_target
        pygame.draw.circle(self.screen, "green", (new_target_x, new_target_y), 10)
        # Go there

    def handleTargetCollision(self):
        """ Does checks for if a ball is colelcted or not and handles that """
        if self.getDistanceToCurrentTarget() < 50:
            if self.currentTarget.targetType == "whiteBall":
                self.ballController.delete_target_at(self.currentTarget)
                print("collected white ball")
                self.storedBalls += 1
            if self.currentTarget.targetType == "orangeBall":
                self.ballController.delete_target_at(self.currentTarget)
                print("collected orange ball")
                self.storedBalls += 1
            if self.currentTarget.targetType == "checkpoint":
                print("reached checkpoint")
            if self.currentTarget.targetType == "goal":
                self.roboController.dropoff()
                print("scored a goal")
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
                smallest_dist = distance

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

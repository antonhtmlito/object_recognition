import math
from roboController import RoboController
from obstacle_controller import Obstacle_Controller
from ballController import BallController
from ray_functions import cast_ray_at_angle
from Target import Target
import time
from Target import Target
import robodetectíon
import pygame

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
        self.last_called = 0

    def handleTick(self):
        """ handles the actions for a given tick in the simulation
        We only want to do certain actions every now and then and we handle this with a timestamp"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_called > 1000:
            print("current time", current_time - self.last_called)

            if self.currentTarget is None:
                print("setting new target")
                self.setCurrentTarget()  # Leave empty to auto calculate best target

            if self.storedBalls >= 4:
                goalpos = robodetectíon.getGoalPosition(self.camera)
                if goalpos is not None:
                    goal_x = goalpos["position"][0] - 150
                    goal_y = goalpos["position"][1]
                    target = Target(targetType="goal", x=goal_x, y=goal_y)
                    pygame.draw.circle(self.screen, "green", (goal_x, goal_y), 10)
                    if self.currentTarget is None:
                        self.currentTarget = target
                    if self.currentTarget.targetType != "goal":
                        self.setCurrentTarget(target)
                    self.driveToCurrentTarget()
            else:
                self.driveToCurrentTarget()
            self.last_called = current_time

    def driveToCurrentTarget(self):
        """ makes the robot drive to the current target """
        if self.handleTargetCollision():
            print("found a target")
            return
        angle = self.getAngleToCurrentTarget()
        if angle is None:
            return
        print("angle to rotate", angle)
        hit = self.checkCollisionsForAngle(angle=angle["angleTarget"]) # for now angle is not used as it is defined elsewhere
        if hit is not None:
            self.handle_detour(angle, hit)
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

    def handle_detour(self, angle, hitPosition):
        """ Creates a checkpoint for the robot to get a better angle for the target """
        max_y = 1080
        max_x = 1920
        # Pick direction
        hit_x = hitPosition[0]
        hit_y = hitPosition[1]

        angle_from_hit_right = angle["angleTarget"] + 90
        angle_from_hit_left = angle["angleTarget"] - 90

        distance_to_center_left = math.dist(
                (hit_x + math.cos(math.radians(angle_from_hit_left)) * 300,
                 hit_x + math.cos(math.radians(angle_from_hit_left)) * 300
                 ),
                (max_x / 2, max_y / 2)
                )

        distance_to_center_right = math.dist(
                (hit_x + math.cos(math.radians(angle_from_hit_right)) * 300,
                 hit_x + math.cos(math.radians(angle_from_hit_right)) * 300
                 ),
                (max_x / 2, max_y / 2)
                )
        if distance_to_center_right > distance_to_center_left:
            angle_from_hit = angle_from_hit_left
        else:
            angle_from_hit = angle_from_hit_right

        new_target_x = hit_x + math.cos(math.radians(angle_from_hit)) * 300
        new_target_y = hit_y + math.sin(math.radians(angle_from_hit)) * 300

        # Create a new target
        new_target = Target(targetType="checkpoint", x=new_target_x, y=new_target_y)
        # self.currentTarget = new_target
        pygame.draw.circle(self.screen, "green", (new_target_x, new_target_y), 10)
        # Go there

    def handleTargetCollision(self):
        """ Does checks for if a ball is colelcted or not and handles that """
        if self.currentTarget is None:
            return False
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
                print("dropping off")
                print(self.robot)
                while self.roboController.busy is True:
                    time.sleep(0.1)
                self.turnToMatchAngle(angleToMatch=0)
                while self.roboController.busy is True:
                    time.sleep(0.1)
                self.roboController.dropoff()
                self.storedBalls = 0
                print("scored a goal")
            self.currentTarget = None
            return True
        else:
            return False

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

    def turnToMatchAngle(self, angleToMatch):
        angle_difference = (angleToMatch - math.degrees(self.robot["rotation"]) + 360) % 360
        angle_difference = angle_difference if angle_difference <= 180 else angle_difference - 360
        time.sleep(2)
        print("turning to match target: ", angle_difference)
        print(self.robot)
        if angle_difference < 0:
            self.roboController.rotate_counterClockwise(abs(angle_difference))
        else:
            self.roboController.rotate_clockwise(abs(angle_difference))
        time.sleep(2)




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


def get_front_corners(player):
    cx, cy = player["x"], player["y"]
    w, h = player["width"], player["height"]
    rotation = player["rotation"]  # in radians

    # Half dimensions
    half_w, half_h = w / 2, h / 2

    # Local coordinates of front corners relative to center
    local_corners = [
        ( half_w, -half_h),  # front-right
        (-half_w, -half_h),  # front-left
    ]

    # Rotate and translate to global coordinates
    corners = []
    for lx, ly in local_corners:
        gx = cx + lx * math.cos(rotation) - ly * math.sin(rotation)
        gy = cy + lx * math.sin(rotation) + ly * math.cos(rotation)
        corners.append((gx, gy))

    return corners

import math
from roboController import RoboController
from obstacle_controller import Obstacle_Controller
from ballController import BallController
from ray_functions import cast_ray_at_angle
from Target import Target
import time
import robodetectíon
import pygame
from values import DEBUG_ROUTING, GOAL_OFFSET, TARGET_DISTANCE_FOR_REMOVING_BALL, ROUTING_UPDATE_INTERVAL

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
        self.last_calledstop = 0
        self.lastTargetTypeGotten = None
        self.seekGoal = False
        self.time_without_target = 0

    def handleTick(self):
        """ handles the actions for a given tick in the simulation
        We only want to do certain actions every now and then and we handle this with a timestamp"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_calledstop > 10:
            if self.currentTarget is not None and self.roboController.driving is True:
                if self.getDistanceToCurrentTarget() < 75:
                    self.roboController.drivestop()
                    self.handleTargetCollision()

        if current_time - self.last_called > ROUTING_UPDATE_INTERVAL:
            print("current time", current_time - self.last_called) if DEBUG_ROUTING else None

            if self.currentTarget is None:
                print("setting new target") if DEBUG_ROUTING else None
                self.setCurrentTarget()  # Leave empty to auto calculate best target

            if self.seekGoal is True:
                goalpos = robodetectíon.getGoalPosition(self.camera)
                if goalpos is not None:
                    goal_x = goalpos["position"][0] - GOAL_OFFSET
                    goal_y = goalpos["position"][1]
                    target = Target(targetType="goal", x=goal_x, y=goal_y, screen=self.screen, mask=self.obstacle_controller.get_obstacles_mask(), wallType="e", walltypeIsLocked=True)
                    pygame.draw.circle(self.screen, "green", (goal_x, goal_y), 20)
                    if self.currentTarget is None:
                        self.currentTarget = target
                    if self.currentTarget.targetType != "goal" and self.currentTarget.targetType != "checkpoint" and self.currentTarget.targetType != "checkpoint":
                        self.currentTarget = target
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

        if self.currentTarget.approach_angle() is not None:
            print("calculating angle") if DEBUG_ROUTING else None
            approach = self.currentTarget.approach_angle()
            if approach is not None and self.lastTargetTypeGotten != "checkpoint":
                angle_rad = math.radians(approach)
                checkpoint_x = self.currentTarget.x + 200 * math.cos(angle_rad)
                checkpoint_y = self.currentTarget.y - 200 * math.sin(angle_rad)
                target = Target(
                    targetType="checkpoint",
                    wallType="free",
                    x=checkpoint_x,
                    y=checkpoint_y,
                    screen=self.screen,
                    mask=self.obstacle_controller.get_obstacles_mask()
                )
                self.currentTarget = target
                pygame.draw.circle(self.screen, "green", (checkpoint_x, checkpoint_y), 5)
            else:
                print("target", self.currentTarget) if DEBUG_ROUTING else None
                print("approach: ", approach) if DEBUG_ROUTING else None

        angle = self.getAngleToCurrentTarget()
        if angle is None:
            return

        print("angle to rotate", angle) if DEBUG_ROUTING else None
        hit = self.checkCollisionsForAngle(angle=angle["angleTarget"]) # for now angle is not used as it is defined elsewhere
        if hit is not None:
            self.handle_detour(angle, hit)
        angle = angle["angleToTurn"]
        print("angle to turn: ", angle) if DEBUG_ROUTING else None
        if -5 < angle < 5:
            print("no angle to turn, driving forward") if DEBUG_ROUTING else None
            if self.currentTarget.approach_angle() is not None:
                if self.roboController.driving is False:
                    self.roboController.drivestart(speed=5)
            elif self.currentTarget.approach_angle() is None:
                distance = self.getDistanceToCurrentTarget()
                speed = distance*0.1+5
                self.roboController.drivestart(speed = speed)


        else:
            if self.roboController.driving is True:
                distance = self.getDistanceToCurrentTarget()
                speed = distance*0.1+5
                self.roboController.drivestart(speed = speed)
                if self.getDistanceToCurrentTarget() < 200:
                    self.roboController.drivestop()
            if angle < 0:
                print("rotate counter") if DEBUG_ROUTING else None
                if self.roboController.driving is False:
                    self.roboController.rotate_counterClockwise(abs(angle))
            elif angle > 0:
                print("rotate") if DEBUG_ROUTING else None
                if self.roboController.driving is False:
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
        new_target = Target(
            targetType="checkpointDetour",
            wallType="free",
            x=new_target_x,
            y=new_target_y,
            screen=self.screen,
            mask=self.obstacle_controller.get_obstacles_mask()
        )
        self.currentTarget = new_target
        pygame.draw.circle(self.screen, "green", (new_target_x, new_target_y), 10)
        # Go there

    def handleTargetCollision(self):
        """ Does checks for if a ball is colelcted or not and handles that """
        if self.currentTarget is None:
            return False
        if self.getDistanceToCurrentTarget() < TARGET_DISTANCE_FOR_REMOVING_BALL:
            if self.currentTarget.targetType == "whiteBall":
                if self.currentTarget.approach_angle is not None:
                    self.backoff_after_target()
                self.ballController.delete_target_at(self.currentTarget)
                print("collected white ball")
                self.lastTargetTypeGotten = "whiteBall"
                self.storedBalls += 1

            if self.currentTarget.targetType == "orangeBall":
                if self.currentTarget.approach_angle is not None:
                    self.backoff_after_target()
                self.ballController.delete_target_at(self.currentTarget)
                print("collected orange ball")
                self.storedBalls += 1
                self.lastTargetTypeGotten = "orangeBall"

            if self.currentTarget.targetType == "checkpoint":
                print("reached checkpoint")
                self.lastTargetTypeGotten = "checkpoint"

            if self.currentTarget.targetType == "checkpointDetour":
                print("reached checkpoint detour")
                self.lastTargetTypeGotten = "checkpointDetour"

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
                self.lastTargetTypeGotten = "goal"

            self.currentTarget = None
            return True
        else:
            return False

    def setRobot(self, robot):
        self.robot = robot

    def backoff_after_target(self):
        while self.roboController.busy is True:
            time.sleep(0.1)
        self.roboController.backward(0.3, 15)

    def setCurrentTarget(self, target=None):
        if target is None:
            if self.ballController.targets == []:
                print("no targets to set current target")
                if self.time_without_target > 10:
                    self.seekGoal = True
                    self.time_without_target = 0
                else:
                    self.time_without_target += 1
            else:
                self.time_without_target = 0
                self.seekGoal = False
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
        print("turning to match target: ", angle_difference) if DEBUG_ROUTING else None
        if angle_difference < 0:
            self.roboController.rotate_counterClockwise(abs(angle_difference))
        else:
            self.roboController.rotate_clockwise(abs(angle_difference))
        time.sleep(2)




    def checkCollisionsForAngle(self, angle):
        hit = cast_ray_at_angle(
                player=self.robot,
                angle=angle,
                max_distance=int(self.getDistanceToCurrentTarget()),
                mask=self.obstacle_controller.get_obstacles_mask(),
                screen=self.screen
                          )

        print("angle to check ray at: ", angle)
        left, right = self.get_sides_for_player(self.robot, angle)

        if hit is None:
            hitLeft = cast_ray_at_angle(
                player=left,
                angle=angle,
                max_distance=int(self.getDistanceToCurrentTarget() * 0.9),
                mask=self.obstacle_controller.get_obstacles_mask(),
                screen=self.screen
            )
            hitRight = cast_ray_at_angle(
                player=right,
                angle=angle,
                max_distance=int(self.getDistanceToCurrentTarget() * 0.9),
                mask=self.obstacle_controller.get_obstacles_mask(),
                screen=self.screen
            )
            if hitLeft is not None and hitRight is not None:
                if hitLeft[2] < hitRight[2]:
                    hit = hitLeft
                else:
                    hit = hitRight
            elif hitLeft is not None:
                hit = hitLeft
            elif hitRight is not None:
                hit = hitRight

        if hit is None:
            return None
        return hit

    def get_sides_for_player(self, player, angle):
        x, y = player["x"], player["y"]
        w = player["width"]
        rotation =  math.radians(angle)
        # rotation = rotation + math.pi / 2 # rotate angle to get the sides instead of the front and back

        left = (x - math.sin(rotation) * w/2, y + w/2 * math.cos(rotation))
        right = (x - math.sin(rotation) * (-w/2), y + (-w/2) * math.cos(rotation))

        pygame.draw.circle(self.screen, "red", (int(left[0]), int(left[1])), 50)
        pygame.draw.circle(self.screen, "blue", (int(right[0]), int(right[1])), 50)
        playerleft = player.copy()
        playerleft["x"] = left[0]
        playerleft["y"] = left[1]
        playerright = player.copy()
        playerright["x"] = right[0]
        playerright["y"] = right[1]

        return (playerleft, playerright)

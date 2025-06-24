from detect_white_and_yellow_ball import get_ball_positions
from collections import defaultdict
from Target import Target
import math
import pygame
from obstacle_controller import Obstacle_Controller
from values import DEBUG_BALLS


# Mostly just a quick adaptations from the target_tracking.py file


class BallController:
    def __init__(self, camera, screen, max_distance=20, promote_after=10, obstacle_controller=None):
        self.camera = camera
        self.screen = screen
        if obstacle_controller is None:
            obstacle_controller = Obstacle_Controller(camera, screen)
        self.mask = obstacle_controller.get_obstacles_mask()
        self.balls = get_ball_positions(camera)
        self.targets = []
        self.target_candidates = defaultdict(dict)
        self.max_distance = max_distance
        self.promote_after = promote_after
        self.last_called = 0

    def handleTick(self, dt=1):
        self.update_ball_positions()
        self.update_target_candidates(self.balls)
        print("balls object", self.balls) if DEBUG_BALLS else None

        for t in self.targets:
            t.age_one_frame()

        seen = [pt for coords in self.balls.values() for pt in coords]
        for t in list(self.targets):
            for (sx, sy) in seen:
                if math.hypot(t.x - sx, t.y - sy) < self.max_distance:
                    t.refresh(sx, sy)   # now sx,sy are in scope
                    break              # don’t refresh more than once per tick

        for t in list(self.targets):
            if t.is_expired():
                self.targets.remove(t)

    def update_ball_positions(self):
        self.balls = get_ball_positions(self.camera)

    def delete_target_at(self, ballPosition):
        """ deletes a target at a given position with the balls position represented as a tuple (x,y)"""
        for target in self.targets[:]:  # weird syntax creates a shallow copy making the iteration not recaclulate when removing an element during
            if math.dist(target.position, ballPosition.position) <= 50:
                self.targets.remove(target)

    def add_target(self, targetType, x, y):
        """ Adds a target to the targets list if it does not already exist"""
        for target in self.targets:
            if target.targetType == targetType and (target.x, target.y) == (x, y):
                return
        target = Target(targetType=targetType, wallType="free", x=x, y=y, screen=self.screen, mask=self.mask )

    def update_target_candidates(self, ball_positions):
        for color_name, coords in ball_positions.items():
            current_frame_hits = set()

            # 1) bump existing candidates or spawn new ones
            for bx, by in coords:
                matched = False
                for (cx, cy), cnt in list(self.target_candidates[color_name].items()):
                    if math.hypot(bx - cx, by - cy) < self.max_distance:
                        self.target_candidates[color_name][(cx, cy)] += 1
                        current_frame_hits.add((cx, cy))
                        matched = True
                        break
                if not matched:
                    self.target_candidates[color_name][(bx, by)] = 1
                    current_frame_hits.add((bx, by))

            # 2) decay unseen candidates
            for pos in list(self.target_candidates[color_name]):
                if pos not in current_frame_hits:
                    self.target_candidates[color_name][pos] -= 1
                    if self.target_candidates[color_name][pos] <= 0:
                        del self.target_candidates[color_name][pos]

            # 3) promote any that hit the threshold
            for pos, hits in list(self.target_candidates[color_name].items()):
                if hits >= self.promote_after:
                    t = Target(targetType=color_name, x=pos[0], y=pos[1], mask=self.mask, screen=self.screen, wallType="free")
                    self.targets.append(t)
                    print(f"🎯 Promoted {t}") if DEBUG_BALLS else None
                    del self.target_candidates[color_name][pos]

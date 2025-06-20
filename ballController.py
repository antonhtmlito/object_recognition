from detect_white_and_yellow_ball import get_ball_positions
from collections import defaultdict
from Target import Target
import math

# Mostly just a quick adaptations from the target_tracking.py file


class BallController:
    def __init__(self, camera, max_distance=200, promote_after=5):
        self.camera = camera
        self.balls = get_ball_positions(camera)
        self.targets = []
        self.target_candidates = defaultdict(dict)
        self.max_distance = max_distance
        self.promote_after = promote_after

    def handleTick(self, dt=1):
        self.update_ball_positions()
        self.update_target_candidates(self.balls)
        print("balls object", self.balls)

        for t in self.targets:
            t.age_one_frame()

        seen = [pt for coords in self.balls.values() for pt in coords]
        for t in list(self.targets):
            if any(math.hypot(t.x - x, t.y - y) < self.max_distance
                   for (x, y) in seen):
                t.refresh()

        for t in list(self.targets):
            if t.is_expired():
                self.targets.remove(t)

    def update_ball_positions(self):
        self.balls = get_ball_positions(self.camera)

    def delete_target_at(self, ballPosition):
        """ deletes a target at a given position with the balls position represented as a tuple (x,y)"""
        for target in self.targets[:]:  # weird syntax creates a shallow copy making the iteration not recaclulate when removing an element during
            print(target.position, ballPosition)
            if math.dist(target.position, ballPosition.position) <= 50:
                self.targets.remove(target)

    def add_target(self, targetType, x, y):
        """ Adds a target to the targets list if it does not already exist"""
        for target in self.targets:
            if target.targetType == targetType and (target.x, target.y) == (x, y):
                return
        target = Target(targetType=targetType, x=x, y=y)

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
                    t = Target(targetType=color_name, x=pos[0], y=pos[1])
                    self.targets.append(t)
                    print(f"🎯 Promoted {t}")
                    del self.target_candidates[color_name][pos]

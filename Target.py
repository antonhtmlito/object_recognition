import math
from ray_functions import cast_rays_from_target

valid_types = ["whiteBall", "orangeBall", "checkpoint", "checkpointDetour", "goal"]
wall_types = ["n", "s", "w", "e", "nw", "ne", "sw", "se", "free"]


class Target:
    wall_approach_angles = {
        "n": 270,
        "e": 180,
        "s": 90,
        "w": 0,
        "ne": 225,
        "nw": 315,
        "se": 135,
        "sw": 45,
        "free": None
    }

    def __init__(self, targetType: str, wallType: str, x: int, y: int, screen, mask, expire_after_frames: int = 20, walltypeIsLocked=False):
        if targetType not in valid_types:
            raise ValueError(f"Invalid target type: {targetType}. Valid types are: {valid_types}")
        if wallType not in wall_types:
            raise ValueError(f"Invalid wall type: {wallType}. Valid types are: {wall_types}")
        self.wallTypeIsLocked = walltypeIsLocked
        self.targetType = targetType
        self.x = x
        self.y = y
        self.position = (x, y)
        self.screen = screen
        self.mask = mask
        self.wallType = wallType
        if self.wallTypeIsLocked is False:
            self.check_wall_ball()

        self.expire_after_frames = expire_after_frames
        self.frames_since_seen = 0

    def __repr__(self):
        return f"Target(type={self.targetType}, position=({self.x}, {self.y}, wall_type={self.wallType}, approach_angle={self.approach_angle()})"

    def check_wall_ball(self):
        ray_results = cast_rays_from_target(
            target={"x": self.x, "y": self.y},
            max_distance=100,
            screen=self.screen,
            mask=self.mask,
        )
        hit_directions = []
        #, 270: "w", 0: "n", 90: "e"
        directions = {0: "e", 90: "s", 180: "w", 270: "n"}

        for angle, hit in zip(directions.keys(), ray_results):
            if hit is not None:
                hit_directions.append(directions[angle])

        if hit_directions != []:
            sorted_hit = ''.join(sorted(hit_directions))
            if sorted_hit in wall_types:
                self.wallType = sorted_hit
            else:
                self.wallType = "free"
        else:
            self.wallType = "free"

    def approach_angle(self):
        return self.wall_approach_angles.get(self.wallType)

    def age_one_frame(self):
        self.frames_since_seen += 1

    def refresh(self, new_x: int, new_y: int):
        self.frames_since_seen = 0
        self.x, self.y = new_x, new_y
        self.position = (new_x, new_y)

        if self.wallTypeIsLocked is False:
            self.check_wall_ball()

    def is_expired(self) -> bool:
        return self.frames_since_seen > self.expire_after_frames

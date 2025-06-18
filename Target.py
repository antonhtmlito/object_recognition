from ray_functions import cast_rays_from_target

valid_types = ["whiteBall", "orangeBall", "checkpoint", "goal"]
wall_types = ["n", "s", "w", "e", "nw", "ne", "sw", "se", "free"]


class Target:
    wall_approach_angles = {
        "n": 0,
        "e": 270,
        "s": 180,
        "w": 90,
        "ne": 315,
        "nw": 45,
        "se": 225,
        "sw": 135,
        "free": None
    }

    def __init__(self, targetType: str, wallType: str, x, y, screen, mask):
        if targetType not in valid_types:
            raise ValueError(f"Invalid target type: {targetType}. Valid types are: {valid_types}")
        if wallType not in wall_types:
            raise ValueError(f"Invalid wall type: {wallType}. Valid types are: {wall_types}")
        self.targetType = targetType
        self.wallType = wallType
        self.x = x
        self.y = y
        self.position = (x, y)
        self.screen = screen
        self.mask = mask


    def __repr__(self):
        return f"Target(type={self.targetType}, position=({self.x}, {self.y}))"

    def check_wall_ball(self):
        ray_results = cast_rays_from_target(
            target={"x": self.x, "y": self.y},
            max_distance=50,
            screen=self.screen,
            mask=self.mask,
        )
        hit_directions = []
        directions = {0: "s", 90: "w", 180: "n", 270: "e"}

        for angle, hit in zip(directions.keys(), ray_results):
            if hit is not None:
                hit_directions.append(directions[angle])

        if hit_directions:
            sorted_hit = ''.join(sorted(hit_directions))
            if sorted_hit in wall_types:
                self.wallType = sorted_hit
            else:
                self.wallType = "free"
        else:
            self.wallType = "free"

    def approach_angle(self):
        return self.wall_approach_angles.get(self.wallType)
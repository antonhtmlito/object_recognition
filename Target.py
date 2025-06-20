import math

valid_types = ["whiteBall", "orangeBall", "checkpoint", "goal"]


class Target:
    def __init__(self, targetType: str, x: int, y: int, expire_after_frames: int = 5):
        if targetType not in valid_types:
            raise ValueError(f"Invalid target type: {targetType}. Valid types are: {valid_types}")
        self.targetType = targetType
        self.x = x
        self.y = y
        self.position = (x, y)

        self.expire_after_frames = expire_after_frames
        self.frames_since_seen = 0

    def age_one_frame(self):
        self.frames_since_seen +=1

    def refresh(self):
        self.frames_since_seen = 0

    def is_expired(self) -> bool:
        return self.frames_since_seen > self.expire_after_frames

    def __repr__(self):
        return (
            f"Target(type={self.targetType}, position=({self.x}, {self.y}), "
            f"age={self.frames_since_seen}/{self.expire_after_frames} frames)"
        )
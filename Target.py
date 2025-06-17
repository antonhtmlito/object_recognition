valid_types = ["whiteBall", "orangeBall", "checkpoint"]


class Target:
    def __init__(self, targetType: str, x, y):
        if targetType not in valid_types:
            raise ValueError(f"Invalid target type: {targetType}. Valid types are: {valid_types}")
        self.targetType = targetType
        self.x = x
        self.y = y
        self.position = (x, y)

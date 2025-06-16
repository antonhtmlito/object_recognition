from dataclasses import dataclass

@dataclass
class Values:
    area_low:   int = 230
    area_high:  int = 270
    radius_low: int = 150
    robot_id:   int = 4
    goal_id:    int = 102


values = Values()

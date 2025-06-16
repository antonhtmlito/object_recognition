import math


class robot:
    def __init__(self, x, y, angleRad, width, height):
        self.x = x
        self.y = y
        self.__angleRad__ = angleRad

    def getAngleDegrees(self):
        return math.degrees(self.__angleRad__)

    def getAngleRadians(self):
        return self.__angleRad__

    def setAngle(self, angleRadian):
        self.__angleRad__ = angleRadian

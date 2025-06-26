#!/usr/bin/env micropython

####
# WE FORGOT TO COPY THE ACTUAL FILE FROM THE ROBOT BEFORE RETURNING IT SO THIS IS A DUPLICATE MADE FROM MEMORY
####
from time import sleep

from socket import *

from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent, MoveTank, MediumMotor
from ev3dev2.sensor import INPUT_4, INPUT_3
from ev3dev2.sensor.lego import GyroSensor, UltrasonicSensor
#from ev3dev2.sensor.lego import TouchSensor
#from ev3dev2.led import Leds

# TODO: Add code here

tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)
sensor = GyroSensor("in1")
distance = UltrasonicSensor("in3")
tank_drive.gyro = sensor
pickup = MediumMotor(OUTPUT_B)

# drive in a turn for 5 rotations of the outer motor
# the first two parameters can be unit classes or percentages.

sensor.mode = "GYRO-ANG"

def driveForward( speed, times):
    tank_drive.on_for_rotations(SpeedPercent(speed), SpeedPercent(speed), times, block = True)
    return 1

def driveBackwards( speed, times):
    tank_drive.on_for_rotations(SpeedPercent(-speed), SpeedPercent(-speed), times, block = True)
    return 1

def rotateClockWise( speed, times):
    tank_drive.on_for_rotations(SpeedPercent(-speed), SpeedPercent(speed), times)
    return 1

def rotateCounterClockWise( speed, times):
    tank_drive.on_for_rotations(SpeedPercent(speed), SpeedPercent(-speed), times)
    return 1

# pickup code
pickup.on(SpeedPercent(-25))
def dropoff():
    pickup.stop()
    pickup.on_for_seconds(SpeedPercent(70), 5, block=True)
    tank_drive.on_for_rotations(80,80, 0.5)
    tank_drive.on_for_rotations(-80,-80, 0.5)
    pickup.on(SpeedPercent(-80))
    return 1

# Code from chapter 2.7.2 computer networking a top down approach

# Code from chapter 2.7.2 computer networking a top down approach
serverPort = 8080
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(1)

print("the server is ready")

try:
    while True:
        print(distance.distance_centimeters)
        connectionSocket, Addr = serverSocket.accept()
        message = connectionSocket.recv(1024).decode()
        # print(message)
        content = message.split("\n")[-1]
        if "," in content:
            content, amount, speed = content.split(",")
        else:
            amount = 1
        print(content)
        print(amount)
        if content == "forward":
            if distance.distance_centimeters < 10:
                print("wall in the way")
                continue
            driveForward(15, float(amount))
            print("driving forward")
            print(amount)
            print(int(float(amount)))

        if content == "backward":
            driveBackwards(50, int(float(amount)))

        if content == "clockwise":
            #rotateClockWise90(50,1)
            tank_drive.turn_degrees(
                    speed=SpeedPercent(speed),
                    target_angle=int(float(amount))
                )


        if content == "counterclockwise":
            #rotateCounterClockWise90(50,1)
            tank_drive.turn_degrees(
                    speed=SpeedPercent(speed),
                    target_angle=-int(float(amount))
                )


        if content == "dropoff":
            dropoff()
            print("dropping off")

        if content == "drivestart":
            tank_drive.on(speed = SpeedPercent(speed))
        
        if content == "drivestop":
            tank_drive.off()

        connectionSocket.send("request completed".encode())
        connectionSocket.close()

finally:
    pickup.stop()   
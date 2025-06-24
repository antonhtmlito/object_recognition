from socket import *
import threading
from values import DEBUG_ROBOT_CONTROLLER


class RoboController:
    def __init__(self, serverName = "172.20.10.3", serverPort = 8080):
        self.serverName = serverName
        self.serverPort = serverPort
        self.busy = False
        self.lock = threading.Lock()
        self.driving = False
        self.send_command("play", "/test/sounds/fein.wav")


    def send_command_threadbound(self, command, entry=None, speed=None):
        with self.lock:
            self.busy = True
            value = entry
            # return  # For debugging purposes, you can remove this line later
            try:
                if speed is not None:
                    message = f"{command}, {entry}, {speed}"  # Ensure correct format with a space after the comma
                else:
                    message = f"{command}"
                print("Sending command:", message) if DEBUG_ROBOT_CONTROLLER else None
                clientSocket = socket(AF_INET, SOCK_STREAM)
                clientSocket.settimeout(10)
                clientSocket.connect((self.serverName, self.serverPort))
                clientSocket.send(message.encode())
                response = clientSocket.recv(1024).decode()
                if response:
                    print(f"Response from server: {response}") if DEBUG_ROBOT_CONTROLLER else None
            except Exception as e:
                print(e)
            finally:
                self.busy = False

    def send_command(self, command, entry=None, speed=None):
        if self.busy is True:
            print("command received and ignored as robot is busy") if DEBUG_ROBOT_CONTROLLER else None
            return False
        thread = threading.Thread(target=self.send_command_threadbound, args=(command, entry, speed), daemon=True)
        thread.start()
        return True

    def forward(self, amount, speed=35):
        self.send_command("forward", amount, speed)
        self.send_command("play", "/test/sounds/pacman_chomp.wav")

    def backward(self, amount, speed=35):
        self.send_command("backward", amount, speed)

    def rotate_clockwise(self, amount, speed=6):
        self.send_command("clockwise", amount, speed)

    def rotate_counterClockwise(self, amount, speed=6):
        self.send_command("counterclockwise", amount, speed)

    def dropoff(self):
        self.send_command("dropoff")
    
    def drivestart(self,speed):
        if self.send_command("drivestart", speed=speed):
            self.driving = True


    def drivestop(self):
        if self.send_command("drivestop"):
            self.driving = False


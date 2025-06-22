from socket import *
import threading
from values import DEBUG_ROBOT_CONTROLLER


class RoboController:
    def __init__(self, serverName = "192.168.0.40", serverPort = 8080):
        self.serverName = serverName
        self.serverPort = serverPort
        self.busy = False
        self.lock = threading.Lock()

    def send_command_threadbound(self, command, entry=None):
        with self.lock:
            self.busy = True
            value = entry
            # return  # For debugging purposes, you can remove this line later
            try:
                if entry is not None:
                    message = f"{command}, {entry}"  # Ensure correct format with a space after the comma
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

    def send_command(self, command, entry=None):
        if self.busy is True:
            print("command recieved and ignored as robot is busy") if DEBUG_ROBOT_CONTROLLER else None
            return
        thread = threading.Thread(target=self.send_command_threadbound, args=(command, entry), daemon=True)
        thread.start()

    def forward(self, amount):
        self.send_command("forward", amount)

    def backward(self, amount):
        self.send_command("backward", amount)

    def rotate_clockwise(self, amount):
        self.send_command("clockwise", amount)

    def rotate_counterClockwise(self, amount):
        self.send_command("counterclockwise", amount)

    def dropoff(self):
        self.send_command("dropoff")

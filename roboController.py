from socket import *


class RoboController:
    def __init__(self, serverName = "172.20.10.2", serverPort = 8080):
        self.serverName = serverName
        self.serverPort = serverPort

    def send_command(self, command, entry):
        value = entry
        print(value)

        message = f"{command}, {value}"  # Ensure correct format with a space after the comma
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((self.serverName, self.serverPort))
        clientSocket.send(message.encode())
        clientSocket.close()

    def forward(self, amount):
        self.send_command("forward", amount)

    def backward(self, amount):
        self.send_command("backward", amount)

    def rotate_clockwise(self, amountRad):
        self.send_command("clockwise", amountRad)

    def rotate_counterClockwise(self, amountRad):
        self.send_command("counterclockwise", amountRad)

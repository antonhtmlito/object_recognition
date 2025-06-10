from socket import *


class RoboController:
    def __init__(self, serverName = "172.20.10.3", serverPort = 8080):
        self.serverName = serverName
        self.serverPort = serverPort

    def send_command(self, command, entry):
        value = entry
        print(value)
        return  # For debugging purposes, you can remove this line later
        try:
            message = f"{command}, {value}"  # Ensure correct format with a space after the comma
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((self.serverName, self.serverPort))
            clientSocket.send(message.encode())
            response = clientSocket.recv(1024).decode()
            if response:
                print(f"Response from server: {response}")
            clientSocket.close()
        except Exception as e:
            ...

    def forward(self, amount):
        self.send_command("forward", amount)

    def backward(self, amount):
        self.send_command("backward", amount)

    def rotate_clockwise(self, amountRad):
        self.send_command("clockwise", amountRad)

    def rotate_counterClockwise(self, amountRad):
        self.send_command("counterclockwise", amountRad)
    
    def dropoff(self):
        self.send_command("dropoff")

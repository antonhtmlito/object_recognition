import socket
from time import sleep
from sounds import play_music_file

def driveForward(speed, times):
    print("driving forward")
    print(times)
    print(int(float(times)))
    return 1

def driveBackwards(speed, times):
    print(f"driveBackwards called with speed={speed}, times={times}")
    return 1

def rotateClockWise(speed, times):
    print(f"rotateClockWise called with speed={speed}, times={times}")
    return 1

def rotateCounterClockWise(speed, times):
    print(f"rotateCounterClockWise called with speed={speed}, times={times}")
    return 1

def dropoff():
    print("dropping off")
    return 1

def rotateClockWise90(speed, times):
    print("sensor calibrated")
    print("sensor reset")
    angle = 0
    while angle < 90:
        print(angle)
        if angle < 50:
            rotateClockWise(50, 0.3)
        elif angle < 70:
            rotateClockWise(50, 0.05)
        elif angle < 90:
            rotateClockWise(50, 0.02)
        angle += 20  # Simulated increment
    print("finished at ")
    print(angle)
    return 1

def rotateCounterClockWise90(speed, times):
    print("sensor calibrated")
    print("sensor reset")
    angle = 0
    while angle < 90:
        print(angle)
        if angle < 50:
            rotateCounterClockWise(50, 0.3)
        elif angle < 70:
            rotateCounterClockWise(50, 0.05)
        elif angle < 90:
            rotateCounterClockWise(50, 0.02)
        angle += 20  # Simulated increment
    print("finished at ")
    print(angle)
    return 1

def start_server(host='', port=8080):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print("the server is ready")
    play_music_file("/test/sounds/fein.wav")

    try:
        while True:
            print("Pretending distance is 15cm")  # Simulate distance check
            connectionSocket, addr = server_socket.accept()
            message = connectionSocket.recv(1024).decode()

            content = message.split("\n")[-1]
            if "," in content:
                content, amount = content.split(",")
            else:
                amount = 1

            print(content)
            print(amount)

            if content == "forward":
                fake_distance = 15  # Simulated obstacle distance
                play_music_file("/test/sounds/pacman_chomp.wav")
                if fake_distance < 10:
                    print("wall in the way")
                else:
                    driveForward(15, float(amount))

            elif content == "backward":
                driveBackwards(50, float(amount))

            elif content == "clockwise":
                print(f"Turning {amount} degrees clockwise")
                # You could call rotateClockWise90(50, 1) here if you want

            elif content == "counterclockwise":
                print(f"Turning {amount} degrees counterclockwise")
                # rotateCounterClockWise90(50, 1)

            elif content == "dropoff":
                dropoff()

            elif content == "playmusic":
                print("Playing test music file asynchronously")
                play_music_file("/test/sounds/fein.wav")

            connectionSocket.send("request completed".encode())
            connectionSocket.close()
    except KeyboardInterrupt:
        print("Server manually stopped.")
    finally:
        print("Server shutting down.")
        server_socket.close()

if __name__ == "__main__":
    start_server()

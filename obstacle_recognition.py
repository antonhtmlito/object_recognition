import cv2
import json
import os
import numpy as np


def load_color_mapping(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Color mapping file not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {file_path}")
        print(f"Details: {str(e)}")
        return None


# Get the color mapping object
script_dir = os.path.dirname(os.path.abspath(__file__))
color_file = os.path.join(script_dir, "colors.json")
colour_mapping = load_color_mapping(color_file)

# Get the obstacle color
obstacle_color = None
if colour_mapping:
    for obj in colour_mapping:
        if obj.get("name") == "obstacle":
            obstacle_color = obj
            print(f"Obstacle color: {obstacle_color}")
            break

if obstacle_color is None:
    print("Error: Obstacle color not found in color mapping")
    exit(1)

# Convert bounds to NumPy arrays
lower_bound = np.array(obstacle_color["colorLowerBound"])
upper_bound = np.array(obstacle_color["colorUpperBound"])

# Open video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video capture")
    exit(1)

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    cv2.imshow("mask", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

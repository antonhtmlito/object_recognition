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
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: Could not open video capture")
    exit(1)


def get_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(frame[y][x])
        tempFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mouseClickColour = tempFrame[y][x]
        print(mouseClickColour)
        lower = mouseClickColour.copy()
        # below mapping is to ensure that the lower bound is not wrapped to the highest value
        hueChange = 12
        SaturationChange = 40
        ValueChange = 75

        if lower[0] < hueChange:
            lower[0] = hueChange + 1
        if lower[1] < SaturationChange:
            lower[1] = SaturationChange + 1
        if lower[2] < ValueChange:
            lower[2] = ValueChange + 1
        np.subtract.at(lower, [0, 1, 2], [hueChange, SaturationChange, ValueChange])

        upper = mouseClickColour.copy()
        # upper mapping is to ensure that the upper bound is not wrapped to the lowest value
        if upper[0] > 255 - hueChange:
            upper[0] = 255 - hueChange - 1
        if upper[1] > 255 - SaturationChange:
            upper[1] = 255 - SaturationChange - 1
        if upper[2] > 255 - ValueChange:
            upper[2] = 255 - ValueChange - 1
        np.add.at(upper, [0, 1, 2], [hueChange, SaturationChange, ValueChange])
        np.clip(upper[0], 0, 180)

        colour_mapping[2]["colorLowerBound"] = lower.tolist()
        colour_mapping[2]["colorUpperBound"] = upper.tolist()
        print(colour_mapping[2])


cv2.namedWindow("frame")
cv2.setMouseCallback("frame", get_color)
cv2.namedWindow("hsv")
cv2.setMouseCallback("hsv", get_color)


# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame")
        break

# Convert bounds to NumPy arrays dupe to remove
    lower_bound = np.array(obstacle_color["colorLowerBound"])
    upper_bound = np.array(obstacle_color["colorUpperBound"])

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    cv2.imshow("hsv", hsv)
    cv2.imshow("mask", mask)
    cv2.imshow("frame", frame)
#    cv2.imwrite('obstacle_mask.png', mask)

    if cv2.waitKey(1) & 0xFF == ord('b'):
        print(frame.shape)
        print(frame[0][0])

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

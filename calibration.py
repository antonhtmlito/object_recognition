import cv2
import json
import os
import numpy as np
from detect_white_and_yellow_ball import warm_frame

print("calibration.py loaded")

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
    global frame

    if event not in [cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN]:
        return

    print("BGR clicked:", frame[y][x])
    temp_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    clicked_hsv = temp_hsv[y][x]
    print("HSV clicked:", clicked_hsv)

    hueChange = 10
    satChange = 100
    valChange = 150

    # Convert to numpy array for math
    hsv_arr = np.array(clicked_hsv, dtype=int)

    # Calculate bounds
    lower = hsv_arr - np.array([hueChange, satChange, valChange])
    upper = hsv_arr + np.array([hueChange, satChange, valChange])


    # Clamp to valid HSV ranges
    lower = np.clip(lower, [0, 0, 0], [179, 255, 255])
    upper = np.clip(upper, [0, 0, 0], [179, 255, 255])

    # Ensure lower is really ≤ upper (in case math makes it invalid)
    lower = np.minimum(lower, upper)
    upper = np.maximum(lower, upper)

    if event == cv2.EVENT_LBUTTONDOWN:
        colour_mapping[2]["colorLowerBound"] = lower.tolist()
        print("✅ Lower bound set to:", lower.tolist())
    elif event == cv2.EVENT_RBUTTONDOWN:
        colour_mapping[2]["colorUpperBound"] = upper.tolist()
        print("✅ Upper bound set to:", upper.tolist())

    # Save immediately
    with open("colors.json", "w") as f:
        json.dump(colour_mapping, f, indent=4)

    print("🧾 Updated config:", colour_mapping[2])


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
    frame = warm_frame(frame, red_gain=0.9, blue_gain=1.1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (15, 15), 0)

    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    # Morphological operations
    kernel = np.ones((4, 4), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    #cv2.imshow("hsv", hsv)
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

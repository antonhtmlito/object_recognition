# detect_white_and_yellow_ball.py

import cv2
import numpy as np
import json

# ──────────────────────────────────────────────────────────────────────────────
# Load object configs from colors.json (your HSV thresholds, etc.)
# ──────────────────────────────────────────────────────────────────────────────
with open("colors.json", "r") as f:
    object_configs = json.load(f)


# ──────────────────────────────────────────────────────────────────────────────
# 1) get_ball_positions(cap)
#
# Reads exactly one frame from `cap`, runs your existing find_balls logic,
# and returns a dict of lists of (x,y) positions for every ball type.
# It does NOT modify or show any windows.
# ──────────────────────────────────────────────────────────────────────────────
def get_ball_positions(cap):
    ret, frame = cap.read()
    if not ret:
        # If the camera read failed, return an empty dict
        return {}

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    ball_positions = {}

    for obj in object_configs:
        name = obj["name"]
        obj_type = obj["type"]

        if obj_type != "ball":
            continue

        lower = np.array(obj["colorLowerBound"])
        upper = np.array(obj["colorUpperBound"])
        mask = cv2.inRange(hsv, lower, upper)

        # (Optional) if you want the same yellow‐exclusion for white balls:
        if "white" in name.lower():
            # yellow_lower = np.array([20, 100, 100])
            # yellow_upper = np.array([40, 255, 255])
            # yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
            # mask = cv2.bitwise_and(mask, cv2.bitwise_not(yellow_mask))
            pass

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        positions = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 100:
                perimeter = cv2.arcLength(cnt, True)
                if perimeter == 0:
                    continue
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
                if circularity > 0.8:
                    ((x, y), radius) = cv2.minEnclosingCircle(cnt)
                    if radius > 10:
                        continue
                    positions.append((int(x), int(y)))

        if positions:
            ball_positions[name] = positions

    return ball_positions


# ──────────────────────────────────────────────────────────────────────────────
# 2) (unchanged) find_balls() and find_obstacles() helpers
# ──────────────────────────────────────────────────────────────────────────────
def find_balls(mask, color_name, color, frame):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = {}
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            if circularity > 0.8:
                ((x, y), radius) = cv2.minEnclosingCircle(cnt)
                if radius > 10:
                    continue

                # Store this (x,y) under the key `color_name`
                detections.setdefault(color_name, []).append((int(x), int(y)))

                # Draw the circle + label on `frame` as before
                cv2.circle(frame, (int(x), int(y)), int(radius), color, 2)
                cv2.putText(
                    frame,
                    f"{color_name} ({int(x)}, {int(y)})",
                    (int(x) - 20, int(y) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )

    return detections

def find_obstacles(mask, name, frame):
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    positions = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 200:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                positions.append((cx, cy))
                cv2.drawContours(frame, [cnt], -1, (0, 0, 255), 2)
                cv2.putText(
                    frame,
                    f"{name} ({cx}, {cy})",
                    (cx - 40, cy - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )
    return positions


# ──────────────────────────────────────────────────────────────────────────────
# 3) Original “live loop” moved under this guard so it DOES NOT run on import
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open camera")
        exit(1)

    # Global HSV for mouse callback
    hsv = None

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE and hsv is not None:
            hsv_val = hsv[y, x]
            print(f"HSV at ({x},{y}): {hsv_val}")

    cv2.namedWindow("Processed Frame")
    cv2.setMouseCallback("Processed Frame", mouse_callback)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        white_mask_display = None  # For optional mask visualization

        for obj in object_configs:
            name = obj["name"]
            obj_type = obj["type"]

            lower = np.array(obj["colorLowerBound"])
            upper = np.array(obj["colorUpperBound"])
            mask = cv2.inRange(hsv, lower, upper)

            # Handle special case for white balls (exclude yellow tones)
            if "white" in name.lower():
                # yellow_lower = np.array([20, 100, 100])
                # yellow_upper = np.array([40, 255, 255])
                # yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
                # mask = cv2.bitwise_and(mask, cv2.bitwise_not(yellow_mask))
                white_mask_display = mask.copy()

            draw_color = (255, 255, 255) if "white" in name.lower() else (0, 140, 255)

            if obj_type == "ball":
                positions = find_balls(mask, name, draw_color, frame)
            else:
                continue

            for pos in positions:
                print(f"{name} detected at: {pos}")

        # Display processed frame
        cv2.imshow("Processed Frame", frame)
        if white_mask_display is not None:
            cv2.imshow("White Mask", white_mask_display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
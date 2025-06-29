# detect_white_and_yellow_ball.py

import cv2
import numpy as np
import json
import values

area_low  = 230
area_high = 270
radius_low = 150
selected_index = 0  


# ──────────────────────────────────────────────────────────────────────────────
# Load object configs from colors.json (your HSV thresholds, etc.)
# ──────────────────────────────────────────────────────────────────────────────
with open("colors.json", "r") as f:
    object_configs = json.load(f)
# ──────────────────────────────────────────────────────────────────────────────
# get the color from mouse picked object
# ──────────────────────────────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────
# Get color range from mouse click
# Left-click updates lower bound, right-click updates upper bound
# ────────────────────────────────────────────────────────────────
def get_color(event, x, y, flags, param):
    global frame, selected_index

    if event not in [cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN]:
        return
    
    cfg = object_configs[selected_index]

    print("BGR clicked:", frame[y][x])
    clicked_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)[y, x]
    print("HSV clicked:", clicked_hsv)

    hueChange = 20
    satChange = 40
    valChange = 100

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
        cfg["colorLowerBound"] = lower.tolist()
        print(f"✅ [{cfg['name']}] lower bound → {lower}")
    elif event == cv2.EVENT_RBUTTONDOWN:
        cfg["colorUpperBound"] = upper.tolist()
        print(f"✅ [{cfg['name']}] upper bound → {upper}")

    # Save immediately
    with open("colors.json","w") as f:
        json.dump(object_configs, f, indent=4)

    print("🧾 Updated config:", object_configs[selected_index])


#warm overlay post process frame
def warm_frame(frame, red_gain=1.1, blue_gain=0.9):
    # Convert to float for precision
    frame = frame.astype(np.float32)
    # Scale R and B channels
    frame[:, :, 2] *= red_gain   # Red channel
    frame[:, :, 0] *= blue_gain  # Blue channel
    # Clip and convert back
    frame = np.clip(frame, 0, 255).astype(np.uint8)
    return frame

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
    
        # Load calibration data

    frame = warm_frame(frame, red_gain=1.2, blue_gain=0.8)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #can be added to smooth edges and blend colors
    hsv = cv2.GaussianBlur(hsv, (7, 7), 0)
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
       # if "white" in name.lower():
            # yellow_lower = np.array([20, 100, 100])
            # yellow_upper = np.array([40, 255, 255])
            # yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
            # mask = cv2.bitwise_and(mask, cv2.bitwise_not(yellow_mask))
        #    pass

        # Morphological operations
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        positions = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if  area > values.values.area_low:
                perimeter = cv2.arcLength(cnt, True)
                if perimeter == 0:
                    continue
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
                if circularity > 0.7:
                    ((x, y), radius) = cv2.minEnclosingCircle(cnt)
                    if radius > values.values.radius_low:
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
        if values.values.area_high < area > values.values.area_low:
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            if circularity > 0.7:
                ((x, y), radius) = cv2.minEnclosingCircle(cnt)
                if radius > values.values.radius_low:
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

    selected_index = 0
    names = [obj["name"] for obj in object_configs]

    # Global HSV for mouse callback
    hsv = None

    #def mouse_callback(event, x, y, flags, param):
    #    if event == cv2.EVENT_MOUSEMOVE and hsv is not None:
    #        hsv_val = hsv[y, x]
    #        print(f"HSV at ({x},{y}): {hsv_val}")

    #cv2.namedWindow("Processed Frame")
    #cv2.setMouseCallback("Processed Frame", mouse_callback)

    cv2.namedWindow("Processed Frame")
    cv2.setMouseCallback("Processed Frame", get_color)
    #cv2.namedWindow("hsv")
    #cv2.setMouseCallback("hsv", get_color)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = warm_frame(frame, red_gain=1.2, blue_gain=0.8)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #can be added to smooth edges and blend colors
        hsv = cv2.GaussianBlur(hsv, (7, 7), 0)
        white_mask_display = None  # For optional mask visualization
        orange_mask_display = None

        for obj in object_configs:
            name = obj["name"]
            obj_type = obj["type"]

            raw_lo = obj["colorLowerBound"]
            raw_hi = obj["colorUpperBound"]

            lower = ( int(raw_lo[0]), int(raw_lo[1]), int(raw_lo[2]) )
            upper = ( int(raw_hi[0]), int(raw_hi[1]), int(raw_hi[2]) )

            mask = cv2.inRange(hsv, lower, upper)

            # Add morphology to clean mask
            kernel = np.ones((2, 2), np.uint8)  # You can tweak kernel size
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # Remove noise
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Close small holes

            # Handle special case for white balls (exclude yellow tones)
            if "white" in name.lower():
                white_mask_display = mask.copy()

            elif "orange" in name.lower():
                orange_mask_display = mask.copy()

            draw_color = (255, 255, 255) if "white" in name.lower() else (0, 140, 255) if "orange" in name.lower() else (0,0,0)

            if obj_type == "ball":
                positions = find_balls(mask, name, draw_color, frame)
            else:
                continue

        #    for pos in positions:
        #        print(f"{name} detected at: {pos}")

        # Display processed frame
        cv2.imshow("Processed Frame", frame)

        if white_mask_display is not None:
            cv2.imshow("White Mask", white_mask_display)


        if orange_mask_display is not None:
            cv2.imshow("Orange Mask", orange_mask_display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('w'):
            selected_index = 1
            print(f"🔘 Now calibrating {names[selected_index]}")
        elif key == ord('o'):
            selected_index = 0
            print(f"🔘 Now calibrating {names[selected_index]}")

        # 3) quit on 'q'
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

import cv2
import numpy as np
import json

with open("colors.json", "r") as f:
    object_configs = json.load(f)

# Open webcam
cap = cv2.VideoCapture(0)

def find_balls(mask, color_name, color, frame):
    """Finds circular balls using contour circularity."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    positions = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue

            circularity = 4 * np.pi * (area / (perimeter * perimeter))

            if circularity > 0.7:  # Filter for roundness
                ((x, y), radius) = cv2.minEnclosingCircle(cnt)
                positions.append((int(x), int(y)))

                # Draw the detected ball
                cv2.circle(frame, (int(x), int(y)), int(radius), color, 2)
                cv2.putText(frame, f"{color_name} ({int(x)}, {int(y)})",
                            (int(x) - 20, int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return positions

def find_obstacles(mask, name, frame):
    """Finds obstacles using bounding boxes (for non-circular objects)."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    positions = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 200:  # Ensures we filter out small noise
            x, y, w, h = cv2.boundingRect(cnt)
            positions.append((x + w // 2, y + h // 2))

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, f"Obstacle ({x+w//2}, {y+h//2})", 
                        (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    return positions

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for obj in object_configs:
        name = obj["name"]
        obj_type = obj["type"]
        lower = np.array(obj["colorLowerBound"])
        upper = np.array(obj["colorUpperBound"])
        mask = cv2.inRange(hsv, lower, upper)

        if obj_type == "ball":
            draw_color = (255, 255, 255) if "white" in name.lower() else (0, 140, 255)
            positions = find_balls(mask, name, draw_color, frame)
        elif obj_type == "obstacle":
            positions = find_obstacles(mask, name, frame)
        else:
            continue

        for pos in positions:
            print(f"{name} detected at: {pos}")

    # Display the frame
    cv2.imshow("Processed Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
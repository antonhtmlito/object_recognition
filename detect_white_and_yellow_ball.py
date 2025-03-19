import cv2
import numpy as np

# Open webcam
cap = cv2.VideoCapture(0)

# Define HSV color ranges
lower_white = np.array([0, 0, 230])  # Very low saturation, very high brightness
upper_white = np.array([180, 20, 255])  # Only allows pure whites

lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([30, 255, 255])

lower_obstacle = np.array([10, 150, 150])
upper_obstacle = np.array([30, 255, 255])

def find_objects(mask, color_name, color, frame):
    """Finds objects in the given mask and draws bounding boxes with labels."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    positions = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:  # Ensures we filter very small noise
            x, y, w, h = cv2.boundingRect(cnt)
            cx, cy = x + w // 2, y + h // 2  # Center coordinates
            positions.append((cx, cy))

            # Draw bounding box and label
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, color_name, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return positions

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create masks for white, yellow balls and obstacles
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    obstacle_mask = cv2.inRange(hsv, lower_obstacle, upper_obstacle)

    # Detect objects
    white_positions = find_objects(white_mask, "White Ball", (255, 255, 255), frame)
    yellow_positions = find_objects(yellow_mask, "Yellow Ball", (0, 255, 255), frame)
    obstacle_positions = find_objects(obstacle_mask, "Obstacle", (0, 0, 255), frame)

    # Show results
    cv2.imshow("Processed Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

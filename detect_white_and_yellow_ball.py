import cv2
import numpy as np

# Open webcam
cap = cv2.VideoCapture(0)

# Definer HSV-farveområder (skal justeres efter lysforhold)
lower_white = np.array([0, 0, 230])  # Very low saturation, very high brightness
upper_white = np.array([180, 20, 255])  # Only allows pure whites

lower_yellow = np.array([5, 100, 100])
upper_yellow = np.array([20, 255, 255])

# Change obstacle color range (e.g., for red or blue obstacles)
lower_obstacle = np.array([0, 150, 100])   # Example for detecting RED obstacles
upper_obstacle = np.array([10, 255, 255])  # Adjust depending on obstacle color

def find_balls(mask, color_name, color, frame):
    """Finds circular balls using contours and minEnclosingCircle()."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    positions = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:  # Ensures we filter out noise
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            if 10 <= radius <= 22:  # Ensures it's about 40mm
                positions.append((int(x), int(y)))

                # Draw the detected ball
                cv2.circle(frame, (int(x), int(y)), int(radius), color, 2)
                cv2.putText(frame, f"{color_name} ({int(x)}, {int(y)})", 
                            (int(x) - 20, int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return positions

def find_obstacles(mask, frame):
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

    # Create masks for white, yellow balls and obstacles
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    obstacle_mask = cv2.inRange(hsv, lower_obstacle, upper_obstacle)

    # Detect objects
    white_positions = find_balls(white_mask, "White Ball", (255, 255, 255), frame)
    yellow_positions = find_balls(yellow_mask, "Yellow Ball", (0, 255, 255), frame)
    obstacle_positions = find_obstacles(obstacle_mask, frame)

    # Print ball locations in real-time
    for pos in white_positions:
        print(f"White Ball Detected at: {pos}")

    for pos in yellow_positions:
        print(f"Yellow Ball Detected at: {pos}")

    for pos in obstacle_positions:
        print(f"Obstacle Detected at: {pos}")

    # Show results
    cv2.imshow("Processed Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows() 
import cv2
import numpy as np

# Open webcam
cap = cv2.VideoCapture(0)

# Define HSV color ranges for yellow and white
lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([30, 255, 255])

lower_white = np.array([0, 0, 180])   # White has low saturation
upper_white = np.array([180, 50, 255])  # High brightness

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create masks for yellow and white
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    # Apply morphological operations to remove noise
    mask_yellow = cv2.erode(mask_yellow, None, iterations=2)
    mask_yellow = cv2.dilate(mask_yellow, None, iterations=2)

    mask_white = cv2.erode(mask_white, None, iterations=2)
    mask_white = cv2.dilate(mask_white, None, iterations=2)

    # Find contours for both colors
    contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_white, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Function to process detected balls and print location
    def detect_ball(contours, frame, color_name, draw_color):
        for contour in contours:
            ((x, y), radius) = cv2.minEnclosingCircle(contour)

            if 18 <= radius <= 22:  # Approximate pixel size for a 40mm ball
                cv2.circle(frame, (int(x), int(y)), int(radius), draw_color, 2)
                cv2.putText(frame, f"{color_name} ({int(x)}, {int(y)})", (int(x) - 30, int(y) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, draw_color, 2)

                # Print ball color and location in console
                print(f"{color_name} Ball Detected at: ({int(x)}, {int(y)})")

    # Detect yellow balls
    detect_ball(contours_yellow, frame, "Yellow", (0, 255, 255))

    # Detect white balls
    detect_ball(contours_white, frame, "White", (255, 255, 255))

    # Show results
    cv2.imshow("Yellow Mask", mask_yellow)
    cv2.imshow("White Mask", mask_white)
    cv2.imshow("Detected Balls", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()

import cv2
import numpy as np

# Open the camera
cap = cv2.VideoCapture(0)  # Change to the correct camera index if needed

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # Adaptive thresholding for better contrast
    _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)

    # Detect circles using Hough Transform
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30,
                               param1=50, param2=30, minRadius=15, maxRadius=25)  # Approx 40mm in pixels

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            x, y, r = circle
            if 38 <= (r * 2) <= 42:  # Filter near 40mm
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                cv2.putText(frame, f"({x}, {y})", (x - 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show the result
    cv2.imshow("Detected Ball", frame)
    cv2.imshow("Threshold", thresh)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()

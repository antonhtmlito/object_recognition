import cv2
import numpy as np

# ─── USER TUNABLE PARAMETERS ──────────────────────────────────────────────

# HoughCircles parameters
DP         = 1.2    # inverse ratio of accumulator resolution to image resolution
MIN_DIST   = 50     # minimum distance between detected centers
PARAM1     = 100    # higher Canny edge threshold (lower is half of this)
PARAM2     = 20     # accumulator threshold: lower values → more false circles
MIN_RADIUS = 10     # minimum circle radius to detect (px)
MAX_RADIUS = 50     # maximum circle radius to detect (px)

# Whether to use the raw frame for detection (False) or first mask to an ROI (True)
USE_ROI_MASK = False

# ───────────────────────────────────────────────────────────────────────────

def main():
    cap = cv2.VideoCapture(0)   # 0 = default camera; change if needed
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Frame capture failed")
            break

        # 1) Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 2) Blur to reduce noise (kernel size and sigma can be tuned)
        blurred = cv2.GaussianBlur(gray, (5, 5), sigmaX=1.5)

        # 3) Edge detection
        edges = cv2.Canny(blurred, threshold1=50, threshold2=150)

        # 4) Hough Circle Transform
        circles = cv2.HoughCircles(
            edges,
            cv2.HOUGH_GRADIENT,
            dp=DP,
            minDist=MIN_DIST,
            param1=PARAM1,
            param2=PARAM2,
            minRadius=MIN_RADIUS,
            maxRadius=MAX_RADIUS
        )


        if circles is not None:
            circles = np.uint16(np.around(circles[0]))
            for (x, y, r) in circles:
                # draw the outer circle
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                # draw the center of the circle
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)

        # 6) Show results
        cv2.imshow("Hough Circle Detection", frame)

        # Quit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
    
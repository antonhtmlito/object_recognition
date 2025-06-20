import cv2
import numpy as np

# === CONFIGURATION ===
CHECKERBOARD = (10, 7)  # Inner corners (columns, rows)
MIN_FRAMES = 10  # Minimum frames to calibrate

# Termination criteria for corner refinement
criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)

# 3D world coordinates for the checkerboard corners
objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

# Arrays to store object and image points
objpoints = []  # 3D points in real world space
imgpoints = []  # 2D points in image plane

cap = cv2.VideoCapture(1)  # Change index if needed
print("Press SPACE to capture a checkerboard frame.")
print("Press ESC when done collecting frames.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret_corners, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    display = frame.copy()
    if ret_corners:
        cv2.drawChessboardCorners(display, CHECKERBOARD, corners, ret_corners)

    cv2.imshow("Calibration Feed", display)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC to exit
        break
    elif key == 32 and ret_corners:  # SPACE to capture
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        objpoints.append(objp.copy())
        imgpoints.append(corners2)
        print(f"[INFO] Captured frame #{len(objpoints)}")

cap.release()
cv2.destroyAllWindows()

# === CALIBRATION ===
if len(objpoints) >= MIN_FRAMES:
    print("\n[INFO] Calibrating camera...")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )

    print("[SUCCESS] Calibration complete!")
    print("Camera matrix:\n", mtx)
    print("Distortion coefficients:\n", dist)

    np.savez("calibration_data.npz", mtx=mtx, dist=dist)

    # === LIVE UNDISTORTED FEED ===
    cap = cv2.VideoCapture(1)
    print("\n[INFO] Showing undistorted live feed (ESC to exit)...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        undistorted = cv2.undistort(frame, mtx, dist, None, newcameramtx)

        cv2.imshow("Undistorted Live Feed", undistorted)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
else:
    print(f"\n[ERROR] Not enough frames captured ({len(objpoints)}). Need at least {MIN_FRAMES}.")
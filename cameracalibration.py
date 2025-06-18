import cv2
import numpy as np
import time

# === CONFIGURATION ===
CHECKERBOARD = (10, 7)  # inner corners
MIN_FRAMES = 30         # how many distinct frames to collect
MAX_FRAMES = 100
MOVEMENT_THRESHOLD = 50  # in pixels (average per-corner movement)
CAPTURE_DELAY = 0.5     # seconds between valid captures

# === INITIALIZATION ===
criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

objpoints = []  # 3D points
imgpoints = []  # 2D image points

cap = cv2.VideoCapture(0)  # Change to 0 or another index if needed
print("Move the checkerboard pattern around. It will auto-capture when changed.")
print(f"Target: {MIN_FRAMES} unique frames. Press ESC to cancel.")

last_capture_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret_corners, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    display = frame.copy()
    if ret_corners:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        should_capture = False

        if len(imgpoints) == 0:
            should_capture = True
        else:
            last = imgpoints[-1].reshape(-1, 2)
            curr = corners2.reshape(-1, 2)
            movement = np.mean(np.linalg.norm(curr - last, axis=1))
            if movement > MOVEMENT_THRESHOLD and time.time() - last_capture_time > CAPTURE_DELAY:
                should_capture = True

        if should_capture:
            objpoints.append(objp.copy())
            imgpoints.append(corners2)
            last_capture_time = time.time()
            print(f"[INFO] Captured frame #{len(objpoints)}")

        cv2.drawChessboardCorners(display, CHECKERBOARD, corners2, ret_corners)

    cv2.imshow("Calibration Feed", display)
    key = cv2.waitKey(1) & 0xFF

    if key == 27 or len(objpoints) >= MAX_FRAMES:
        break

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

    # Optional live test
    print("\n[INFO] Showing undistorted live feed (ESC to exit)...")
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        h, w = frame.shape[:2]
        newcameramtx, _ = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        undistorted = cv2.undistort(frame, mtx, dist, None, newcameramtx)
        cv2.imshow("Undistorted Feed", undistorted)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
else:
    print(f"[ERROR] Not enough frames captured ({len(objpoints)}). Need at least {MIN_FRAMES}.")

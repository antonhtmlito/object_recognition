import cv2
import numpy as np

CHECKERBOARD = (10, 7)
MIN_FRAMES = 30

criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)
objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

objpoints = []
imgpoints = []

cap = cv2.VideoCapture(1)
print("Move the checkerboard pattern around. Press ESC to stop.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret_corners, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    display = frame.copy()
    if ret_corners:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        
        # Check if this frame is “new” enough to add (e.g. not too close to last one)
        if len(imgpoints) == 0 or cv2.norm(corners2 - imgpoints[-1]) > 1000:
            objpoints.append(objp.copy())
            imgpoints.append(corners2)
            print(f"[INFO] Captured frame #{len(objpoints)}")

        cv2.drawChessboardCorners(display, CHECKERBOARD, corners2, ret_corners)

    cv2.imshow("Calibration Feed", display)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()

if len(objpoints) >= MIN_FRAMES:
    print("[INFO] Calibrating camera...")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )
    print("[SUCCESS] Calibration complete!")
    np.savez("calibration_data.npz", mtx=mtx, dist=dist)
else:
    print(f"[ERROR] Not enough frames captured ({len(objpoints)}). Need at least {MIN_FRAMES}.")

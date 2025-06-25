import cv2
import numpy as np
import os

# === CONFIGURATION ===
CHECKERBOARD = (10, 7)  # Inner corners (columns, rows)
MIN_FRAMES = 10
SAVE_DIR = "calib_images"
os.makedirs(SAVE_DIR, exist_ok=True)

criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)

objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

# === STEP 1: Capture and Save Frames ===
cap = cv2.VideoCapture(0)
print("Press SPACE to save a checkerboard image.")
print("Press ESC to finish capturing.")

capture_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret_corners, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

    display = frame.copy()
    if ret_corners:
        cv2.drawChessboardCorners(display, CHECKERBOARD, corners, ret_corners)

    cv2.imshow("Capture Checkerboard", display)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC
        break
    elif key == 32 and ret_corners:  # SPACE
        filename = os.path.join(SAVE_DIR, f"frame_{capture_count:02d}.jpg")
        cv2.imwrite(filename, frame)
        print(f"[INFO] Saved {filename}")
        capture_count += 1

cap.release()
cv2.destroyAllWindows()

# === STEP 2: Calibration from Saved Images ===
if capture_count >= MIN_FRAMES:
    print("\n[INFO] Starting calibration...")
    objpoints = []
    imgpoints = []

    images = sorted([f for f in os.listdir(SAVE_DIR) if f.endswith(".jpg")])

    for fname in images:
        img = cv2.imread(os.path.join(SAVE_DIR, fname))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret_corners, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)
        if ret_corners:
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
            objpoints.append(objp.copy())
            imgpoints.append(corners2)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )

    print("[SUCCESS] Calibration complete!")
    print("Camera matrix:\n", mtx)
    print("Distortion coefficients:\n", dist)

    np.savez("calibration_data.npz", mtx=mtx, dist=dist)

    # === Reprojection Error Calculation ===
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
    mean_error += error

mean_error /= len(objpoints)
print(f"[INFO] Average reprojection error: {mean_error:.4f} pixels")

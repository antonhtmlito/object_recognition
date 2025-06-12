import cv2
import numpy as np
import math

# Dine corner-IDs
CORNER_IDS = {110, 120, 130, 140}
ROBOT_ID = 1

def get_arena_corners(frame, camera_mtx=None, dist_coeffs=None):
    if camera_mtx is not None and dist_coeffs is not None:
        frame = cv2.undistort(frame, camera_mtx, dist_coeffs)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    params = cv2.aruco.DetectorParameters()

    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=params)
    if ids is None:
        return {}

    ids = ids.flatten()
    pts = {}
    for corner, mid in zip(corners, ids):
        if mid in CORNER_IDS:
            c = corner.reshape((4, 2))
            center = c.mean(axis=0).astype(int)
            pts[mid] = tuple(center)

    return pts

def get_robot_position(frame, robot_id=ROBOT_ID):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    params = cv2.aruco.DetectorParameters()

    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=params)

    if ids is None:
        return None

    ids = ids.flatten()

    for corner, mid in zip(corners, ids):
        if mid == robot_id:
            c = corner.reshape((4, 2))
            center = c.mean(axis=0).astype(int)
            return tuple(center)

    return None

def is_inside_arena(point, arena_polygon):
    contour = np.array(arena_polygon, dtype=np.int32)
    return cv2.pointPolygonTest(contour, point, False) >= 0


def detect_and_draw_arena(frame, camera_mtx=None, dist_coeffs=None):
    out = frame.copy()

    gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    params = cv2.aruco.DetectorParameters()
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=params)

    if ids is not None:
        cv2.aruco.drawDetectedMarkers(out, corners, ids, (255, 0, 0))

    pts = get_arena_corners(frame, camera_mtx, dist_coeffs)

    if set(pts.keys()) == CORNER_IDS:
        vals = np.array(list(pts.values()))
        cx, cy = vals[:, 0].mean(), vals[:, 1].mean()

        order = sorted(pts.keys(), key=lambda mid: math.atan2(pts[mid][1] - cy, pts[mid][0] - cx))
        polygon = [pts[mid] for mid in order] + [pts[order[0]]]

        cv2.polylines(out, [np.array(polygon, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=3)

        robot_pos = get_robot_position(frame)
        if robot_pos:
            robot_pos = tuple(map(int, robot_pos))
            if is_inside_arena(tuple(robot_pos), polygon):
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
                print("Robot uden for arenaen!")

            cv2.circle(out, robot_pos, 10, color, -1)

    return out

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    try:
        mtx = np.load("camera_mtx.npy")
        dist = np.load("dist_coeffs.npy")
    except FileNotFoundError:
        mtx = dist = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        out = detect_and_draw_arena(frame, camera_mtx=mtx, dist_coeffs=dist)
        cv2.imshow("ArUco Arena", out)

        if cv2.waitKey(1) & 0xFF in (27, ord('q')):
            break

    cap.release()
    cv2.destroyAllWindows()

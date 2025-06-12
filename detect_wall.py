import cv2
import numpy as np

# 1) Load kalibrering
data = np.load("camera_calib.npz")
K, dist = data["K"], data["dist"]

# 2) Opsæt ArUco
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
param    = cv2.aruco.DetectorParameters_create()
marker_length = 0.10  # meter
corner_ids = [0,1,2,3]

def detect_wall_polygon(frame):
    """
    Retunerer hull-polygon (Nx1x2 float32) i world-plane (x,y) meter-koordinater.
    Hvis der ikke findes alle 4 corners, returnér None.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=param)
    if ids is None:
        return None

    # Pose-estimat for alle fundne markører
    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
        corners, marker_length, K, dist
    )

    # Filtrér kun hjørne-IDs
    pts = []
    for i, mid in enumerate(ids.flatten()):
        if mid in corner_ids:
            # tvecs[i][0] = [x, y, z] i meter i kameraplan
            x, y, z = tvecs[i][0]
            # Kameraet sidder lodret, så z ≃ 1.7 (højde) og (x,y) er gulvplan
            pts.append([x, y])

    if len(pts) < 4:
        return None

    # Lav convex hull for at sikre rigtig rækkefølge og undgå kryds
    pts = np.array(pts, dtype=np.float32)
    hull = cv2.convexHull(pts)
    # hull har form (4,1,2) – klar til cv2.pointPolygonTest
    return hull

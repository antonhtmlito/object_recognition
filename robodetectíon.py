import cv2
import numpy as np


def calcAngle(corners):
    middle = np.mean(corners, axis=0)
    mean = np.mean(np.array((corners[1], corners[2])), axis=0)

    corner_for_measure = corners[0]
    corner_for_measure = mean
    dx = corner_for_measure[0] - middle[0]
    dy = corner_for_measure[1] - middle[1]

    angle_rad = np.arctan2(dy, dx)
    angle_deg = np.degrees(angle_rad)
    angle_deg = (angle_deg + 360) % 360
    return angle_deg


def getBotPosition(camera):
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    ret, frame = camera.read()
    if not ret:
        raise Exception("Can't get frame")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = detector.detectMarkers(gray)
    angle = ""
    if ids is not None:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        marker_corners = corners[0][0]
        angle = calcAngle(marker_corners)

    # Only works for single marker
    mean = np.mean(corners[0][0], axis=0) if len(corners) != 0 else ""
    frame = cv2.putText(frame, str(mean), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    frame = cv2.putText(frame, str(angle), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.imshow('Detected Markers', frame)
    if angle != "":
        return {"position": mean.tolist(), "angle": angle}


if __name__ == "__main__":
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        raise Exception("camera not openened")
    while True:
        getBotPosition(cap)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

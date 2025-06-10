import cv2
import cv2.aruco as aruco
import numpy as np

# Markør-ID'er
målA_id = 101
målB_id = 102


# ArUco dictionary
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_1000)
parameters = aruco.DetectorParameters()

# Kamera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Find markører
    corners, ids, _ = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

    target_coordinates = {}

    # Tegn alle fundne markører
    if ids is not None:
        ids = ids.flatten()
        aruco.drawDetectedMarkers(frame, corners, ids)

        marker_centers = {}
        mål_firkanter = {}


        # Beregn center for hver markør
        for i, id_val in enumerate(ids):
            c = corners[i][0]
            cx = int(c[:, 0].mean())
            cy = int(c[:, 1].mean())
            marker_centers[id_val] = (cx, cy)
            if id_val in [målA_id, målB_id]:
                mål_firkanter[id_val] = corners[i][0]

            # Skriv ID på billedet
            cv2.putText(frame, f"ID:{id_val}", (cx - 10, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Tegn mål
            if målA_id in marker_centers:
                cv2.circle(frame, marker_centers[målA_id], 10, (0, 0, 255), -1)
                cv2.putText(frame, "Mål A", (marker_centers[målA_id][0] + 10, marker_centers[målA_id][1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            if målB_id in marker_centers:
                cv2.circle(frame, marker_centers[målB_id], 10, (255, 0, 0), -1)
                cv2.putText(frame, "Mål B", (marker_centers[målB_id][0] + 10, marker_centers[målB_id][1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            if target_coordinates:
                print("Target Coordinates:", target_coordinates)

    cv2.imshow("Banetegning via ArUco", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
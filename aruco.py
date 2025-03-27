import cv2
import numpy as np

def detect_aruco_markers():
    # Initialize the camera
    cap = cv2.VideoCapture(2)


    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    # Create ArUco dictionary (6x6 with 250 markers)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()

    # Create the ArUco detector
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    try:
        while True:
            # Read frame from camera
            ret, frame = cap.read()
            if not ret:
                print("Error: Can't receive frame")
                break

            # Convert frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect the markers
            corners, ids, rejected = detector.detectMarkers(gray)

            # If markers are detected
            if ids is not None:
                # Draw detected markers
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)

                # Print the detected markers
                print("Detected markers:", ids)

                # If exactly 3 markers are detected, draw a rectangle and triangle
                if len(ids) == 3:
                    # Get the centers of the markers
                    centers = []
                    for corner in corners:
                        center = np.mean(corner[0], axis=0)
                        centers.append(center)

                    # Convert centers to numpy array
                    centers = np.array(centers, dtype=np.int32)

                    # Find the bounding rectangle
                    x, y, w, h = cv2.boundingRect(centers)

                    # Draw the rectangle
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Draw lines between markers to show triangle
                    for i in range(3):
                        pt1 = tuple(centers[i])
                        pt2 = tuple(centers[(i + 1) % 3])
                        cv2.line(frame, pt1, pt2, (0, 0, 255), 2)

            # Display the frame
            cv2.imshow('Detected Markers', frame)

            # Break loop on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    detect_aruco_markers()

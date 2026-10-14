"""
camera_to_table.py  -  Phase 3, Week 8: turn camera pixels into robot coordinates.

Setup: tape a sheet of letter paper (11 x 8.5 in) to your desk and point the
webcam at it from above at an angle. The paper becomes the robot's workspace:
its four corners map to four points on the simulated counter.

Calibrate once:  python src/camera_to_table.py
  Click the 4 paper corners in this order:  far-left, far-right, near-right, near-left.
  ("far" = the edge farthest from you.) The result is saved to calibration.json.

The math is a "homography": a 3x3 matrix that maps one flat plane (the image)
onto another flat plane (the table), correcting for the camera's tilt.
"""
import json
from pathlib import Path

import cv2
import numpy as np

CALIBRATION_FILE = Path(__file__).parent.parent / "calibration.json"

# Where the paper's corners land in the simulated kitchen (metres, robot base = 0,0).
# Same order as you click: far-left, far-right, near-right, near-left.
ROBOT_CORNERS = [(0.65, 0.25), (0.65, -0.10), (0.35, -0.10), (0.35, 0.25)]


def pixel_to_robot(matrix, u, v):
    """Map one image pixel (u, v) to robot (x, y) using the homography matrix."""
    point = np.array([[[u, v]]], dtype=np.float32)
    x, y = cv2.perspectiveTransform(point, matrix)[0][0]
    return float(x), float(y)


def load_matrix():
    return np.array(json.loads(CALIBRATION_FILE.read_text())["matrix"], dtype=np.float32)


def calibrate():
    cam = cv2.VideoCapture(0)
    ok, frame = cam.read()
    cam.release()
    if not ok:
        raise SystemExit("No camera image - check the camera permission")

    clicks = []

    def on_click(event, u, v, *_):
        if event == cv2.EVENT_LBUTTONDOWN and len(clicks) < 4:
            clicks.append((u, v))
            cv2.circle(frame, (u, v), 6, (0, 0, 255), -1)
            cv2.imshow("Click the 4 paper corners", frame)

    cv2.imshow("Click the 4 paper corners", frame)
    cv2.setMouseCallback("Click the 4 paper corners", on_click)
    while len(clicks) < 4:
        cv2.waitKey(50)
    cv2.destroyAllWindows()

    matrix = cv2.getPerspectiveTransform(np.float32(clicks), np.float32(ROBOT_CORNERS))
    CALIBRATION_FILE.write_text(json.dumps({"clicks": clicks, "matrix": matrix.tolist()}, indent=2))
    print("Saved", CALIBRATION_FILE)
    print("Check: the first corner maps to", pixel_to_robot(matrix, *clicks[0]))


if __name__ == "__main__":
    calibrate()

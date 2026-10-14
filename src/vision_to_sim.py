"""
vision_to_sim.py  -  Phase 3, Week 9: real objects on your desk appear in the simulation.

Put a real apple, orange, carrot... on the paper, then run:
    python src/vision_to_sim.py
Every second the camera looks, YOLO finds the food, the homography converts its
position to robot coordinates, and the simulated kitchen updates to match.
Press q in the camera window to quit.
"""
import time

import cv2
from ultralytics import YOLO

from camera_to_table import load_matrix, pixel_to_robot
from kitchen_sim import KitchenSim

FOODS = {"apple", "orange", "banana", "broccoli", "carrot"}


def detect_food(model, frame, matrix):
    """Return [{"name", "x", "y"}] in robot coordinates for each food the camera sees."""
    found = []
    for box in model(frame, device="mps", verbose=False)[0].boxes:
        name = model.names[int(box.cls)]
        if name in FOODS and float(box.conf) > 0.4:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            u, v = (x1 + x2) / 2, y2        # bottom-centre of the box = where it touches the table
            x, y = pixel_to_robot(matrix, u, v)
            found.append({"name": name, "x": round(x, 3), "y": round(y, 3)})
    return found


if __name__ == "__main__":
    model, matrix = YOLO("yolo11n.pt"), load_matrix()
    sim = KitchenSim(gui=True, start_with_food=False)
    cam = cv2.VideoCapture(0)
    last = 0.0
    while True:
        ok, frame = cam.read()
        if not ok:
            break
        if time.time() - last > 1.0:
            detections = detect_food(model, frame, matrix)
            sim.sync_objects(detections)
            print(detections)
            last = time.time()
        sim.step()
        cv2.imshow("Camera (q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cam.release()

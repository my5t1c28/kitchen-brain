"""
webcam_yolo.py  -  Phase 3, Week 7: see food through the webcam with YOLO.

Run:  python src/webcam_yolo.py        (press q to quit)

The first run downloads the small YOLO model (~6 MB). On a Mac, device="mps"
uses the Apple GPU. macOS will ask for camera permission for your Terminal app -
allow it in System Settings > Privacy & Security > Camera.
"""
import cv2
from ultralytics import YOLO

KITCHEN_THINGS = {"apple", "orange", "banana", "broccoli", "carrot",
                  "bowl", "cup", "bottle", "knife", "fork", "spoon", "sandwich"}

model = YOLO("yolo11n.pt")
cam = cv2.VideoCapture(0)

while True:
    ok, frame = cam.read()
    if not ok:
        print("No camera image - check the camera permission")
        break
    result = model(frame, device="mps", verbose=False)[0]
    for box in result.boxes:
        name = model.names[int(box.cls)]
        conf = float(box.conf)
        if name in KITCHEN_THINGS and conf > 0.4:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{name} {conf:.0%}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("Kitchen camera (q to quit)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cam.release()
cv2.destroyAllWindows()

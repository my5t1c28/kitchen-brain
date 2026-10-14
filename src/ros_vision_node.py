"""
ros_vision_node.py  -  Phase 3: the "Sensors" node. Publishes what the webcam sees.

Publishes  /detections  (JSON list like [{"name": "apple", "x": 0.5, "y": 0.1}]) once per second
Run (after calibrating with camera_to_table.py):  python src/ros_vision_node.py
"""
import json

import cv2
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from ultralytics import YOLO

from camera_to_table import load_matrix
from vision_to_sim import detect_food


class VisionNode(Node):
    def __init__(self):
        super().__init__("vision_node")
        self.model, self.matrix = YOLO("yolo11n.pt"), load_matrix()
        self.cam = cv2.VideoCapture(0)
        self.pub = self.create_publisher(String, "detections", 10)
        self.create_timer(1.0, self.look)

    def look(self):
        ok, frame = self.cam.read()
        if not ok:
            self.get_logger().warn("No camera image")
            return
        found = detect_food(self.model, frame, self.matrix)
        self.pub.publish(String(data=json.dumps(found)))
        self.get_logger().info(f"I see: {found}")


def main():
    rclpy.init()
    rclpy.spin(VisionNode())


if __name__ == "__main__":
    main()

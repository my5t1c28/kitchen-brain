"""
ros_arm_node.py  -  Phase 2: the "Motors" node. Owns the simulated robot arm.

Listens on  /arm_command    (JSON like {"action": "pick", "object": "apple"})
            /detections     (JSON list from the camera node - Phase 3)
Publishes   /objects        (JSON list of object names in the kitchen, once per second)
            /arm_status     (text updates like "done: pick apple")

Run (inside `pixi shell`):  python src/ros_arm_node.py
"""
import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from kitchen_sim import KitchenSim


class ArmNode(Node):
    def __init__(self):
        super().__init__("arm_node")
        self.sim = KitchenSim(gui=True)
        self.status = self.create_publisher(String, "arm_status", 10)
        self.objects = self.create_publisher(String, "objects", 10)
        self.create_subscription(String, "arm_command", self.on_command, 50)
        self.create_subscription(String, "detections", self.on_detections, 10)
        self.create_timer(1 / 60, self.sim.step)            # keep physics running
        self.create_timer(1.0, self.publish_objects)
        self.get_logger().info("Arm ready")

    def say(self, text):
        self.status.publish(String(data=text))
        self.get_logger().info(text)

    def publish_objects(self):
        self.objects.publish(String(data=json.dumps(list(self.sim.objects))))

    def on_detections(self, msg):
        self.sim.sync_objects(json.loads(msg.data))

    def on_command(self, msg):
        cmd = json.loads(msg.data)
        try:
            if cmd["action"] == "pick":
                self.sim.pick(cmd["object"])
            elif cmd["action"] == "place_in_bowl":
                self.sim.place_in_bowl()
            else:
                raise ValueError(f"unknown action {cmd['action']}")
            self.say(f"done: {cmd['action']} {cmd.get('object', '')}")
        except Exception as error:
            self.say(f"FAILED: {cmd} ({error})")


def main():
    rclpy.init()
    rclpy.spin(ArmNode())


if __name__ == "__main__":
    main()

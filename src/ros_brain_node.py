"""
ros_brain_node.py  -  Phase 2 & 4: the "Brain" node. Turns a task into arm commands.

Listens on  /task         (text, e.g. "put the apple in the bowl")
            /objects      (what's in the kitchen, from the arm node)
Publishes   /arm_command  (one JSON command per step)

Phase 2 (simple rules):   python src/ros_brain_node.py
Phase 4 (local LLM):      python src/ros_brain_node.py --llm

Send it a task from another terminal:
    Phase 2:  ros2 topic pub --once /task std_msgs/msg/String "{data: 'put the apple and the carrot in the bowl'}"
    Phase 4:  ros2 topic pub --once /task std_msgs/msg/String "{data: 'make me a fruit salad'}"
"""
import json
import sys

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class BrainNode(Node):
    def __init__(self, use_llm):
        super().__init__("brain_node")
        self.use_llm = use_llm
        self.known_objects = []
        self.commands = self.create_publisher(String, "arm_command", 50)
        self.create_subscription(String, "objects", self.on_objects, 10)
        self.create_subscription(String, "task", self.on_task, 10)
        self.get_logger().info(f"Brain ready ({'LLM' if use_llm else 'rules'} mode)")

    def on_objects(self, msg):
        self.known_objects = json.loads(msg.data)

    def rule_based_plan(self, task):
        """Phase 2: pick every known object whose name appears in the sentence."""
        steps = []
        for name in self.known_objects:
            if name in task.lower():
                steps += [{"action": "pick", "object": name}, {"action": "place_in_bowl"}]
        return steps

    def llm_plan(self, task):
        """Phase 4: ask the local LLM, then validate before anything moves."""
        from llm_planner import ask_llm, validate_plan
        plan = ask_llm(task, self.known_objects)
        self.get_logger().info(f"LLM says: {plan.reasoning}")
        problems = validate_plan(plan, self.known_objects)
        if problems:
            self.get_logger().warn(f"Plan rejected: {problems}")
            return []
        return [step.model_dump() for step in plan.steps]

    def on_task(self, msg):
        task = msg.data
        self.get_logger().info(f"Task: {task}")
        steps = self.llm_plan(task) if self.use_llm else self.rule_based_plan(task)
        if not steps:
            self.get_logger().warn("No steps to run")
        for step in steps:
            self.commands.publish(String(data=json.dumps(step)))
            self.get_logger().info(f"  -> {step}")


def main():
    rclpy.init()
    rclpy.spin(BrainNode(use_llm="--llm" in sys.argv))


if __name__ == "__main__":
    main()

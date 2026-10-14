# Kitchen Brain

An AI "brain" for a simulated kitchen robot arm. You type *"make me a fruit salad"*, a local
language model plans the steps, a webcam finds the real food on the desk, and a simulated
Franka Panda arm picks the items and puts them in a bowl.

```
 Webcam ──► vision node ──/detections──► arm node (PyBullet sim) ◄──/arm_command── brain node ◄── "make a salad"
 (YOLO + homography)                         │                                      (rules → local LLM)
                                             └──────────────/objects───────────────────►
```

| File | Phase | What it does |
|---|---|---|
| `src/week1_two_link_arm.py` | 1 | Forward/inverse kinematics of a 2-joint arm, by hand |
| `src/kitchen_sim.py` | 1 | The simulated kitchen and the robot's skills: `pick`, `place_in_bowl` |
| `src/ros_arm_node.py` | 2 | ROS 2 node that owns the robot arm |
| `src/ros_brain_node.py` | 2, 4 | ROS 2 node that turns a task into arm commands |
| `src/webcam_yolo.py` | 3 | Live food detection with YOLO |
| `src/camera_to_table.py` | 3 | Calibrates camera pixels → robot coordinates |
| `src/vision_to_sim.py` | 3 | Real food on the desk appears in the simulation |
| `src/ros_vision_node.py` | 3 | ROS 2 node that publishes what the camera sees |
| `src/llm_planner.py` | 4 | Local LLM (Ollama) planner with safety validation |

Built on a MacBook (Apple M5, 32 GB) with PyBullet, ROS 2 Jazzy (RoboStack), OpenCV, Ultralytics YOLO and Ollama.
See `docs/journal.md` for the engineering log.

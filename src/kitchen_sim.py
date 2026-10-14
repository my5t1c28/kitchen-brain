"""
kitchen_sim.py  -  The simulated kitchen used by every phase of the project.

A Franka Panda robot arm stands on a "counter" (the floor plane).
Small colored blocks stand in for food (apple, orange, broccoli, carrot)
and a tray stands in for the salad bowl.

Run it directly to watch a pick-and-place demo:
    python src/kitchen_sim.py
"""
import math
import time

import pybullet as p
import pybullet_data

# ---- Robot constants for the Franka Panda model bundled with PyBullet ----
ARM_JOINTS = [0, 1, 2, 3, 4, 5, 6]      # the 7 rotating joints of the arm
FINGER_JOINTS = [9, 10]                  # the two gripper fingers
EE_LINK = 11                             # "grasp target" point between the fingers
HOME_POSE = [0.0, -0.4, 0.0, -2.4, 0.0, 2.0, 0.8]
GRIPPER_DOWN = p.getQuaternionFromEuler([math.pi, 0, 0])  # fingers pointing at the counter

# ---- Colors for foods. Names match what the YOLO camera model can recognise ----
COLORS = {
    "apple":    [0.85, 0.10, 0.10, 1],
    "orange":   [1.00, 0.55, 0.00, 1],
    "broccoli": [0.20, 0.70, 0.20, 1],
    "carrot":   [1.00, 0.40, 0.10, 1],
    "banana":   [0.95, 0.85, 0.10, 1],
}
# ---- Starting layout: name -> (x, y) position on the counter in metres ----
FOOD = {
    "apple":    (0.45,  0.15),
    "orange":   (0.55,  0.05),
    "broccoli": (0.45, -0.05),
    "carrot":   (0.60,  0.20),
}
BOWL_XY = (0.40, -0.35)


class KitchenSim:
    def __init__(self, gui=True, start_with_food=True):
        self.client = p.connect(p.GUI if gui else p.DIRECT)
        self.gui = gui
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.loadURDF("plane.urdf")
        self.robot = p.loadURDF("franka_panda/panda.urdf", [0, 0, 0], useFixedBase=True)
        self.bowl = p.loadURDF("tray/traybox.urdf", [BOWL_XY[0], BOWL_XY[1], 0], globalScaling=0.6)
        self.objects = {}
        if start_with_food:
            for name, xy in FOOD.items():
                self.add_object(name, xy)
        self._grasp = None          # constraint id while holding something
        self._bowl_items = 0        # so items in the bowl don't stack on each other
        self.reset_arm()

    # ---------- setting up the scene ----------
    def add_object(self, name, xy):
        """Put a 5 cm block called `name` on the counter at (x, y)."""
        body = p.loadURDF("cube_small.urdf", [xy[0], xy[1], 0.03])
        p.changeVisualShape(body, -1, rgbaColor=COLORS.get(name, [0.6, 0.6, 0.6, 1]))
        self.objects[name] = body
        return body

    def reset_arm(self):
        for joint, angle in zip(ARM_JOINTS, HOME_POSE):
            p.resetJointState(self.robot, joint, angle)
        self.open_gripper(steps=1)

    # ---------- low-level motion ----------
    def step(self, n=1):
        for _ in range(n):
            p.stepSimulation()
            if self.gui:
                time.sleep(1 / 240)

    def move_to(self, xyz, steps=240):
        """Move the gripper to a point (x, y, z) in metres using inverse kinematics."""
        angles = p.calculateInverseKinematics(
            self.robot, EE_LINK, xyz, GRIPPER_DOWN,
            maxNumIterations=200, residualThreshold=1e-4)
        p.setJointMotorControlArray(
            self.robot, ARM_JOINTS, p.POSITION_CONTROL,
            targetPositions=angles[:7], forces=[200] * 7)
        self.step(steps)

    def gripper_position(self):
        return p.getLinkState(self.robot, EE_LINK)[4]

    def open_gripper(self, steps=60):
        p.setJointMotorControlArray(self.robot, FINGER_JOINTS, p.POSITION_CONTROL,
                                    targetPositions=[0.04, 0.04], forces=[50, 50])
        self.step(steps)

    def close_gripper(self, steps=60):
        p.setJointMotorControlArray(self.robot, FINGER_JOINTS, p.POSITION_CONTROL,
                                    targetPositions=[0.0, 0.0], forces=[50, 50])
        self.step(steps)

    # ---------- high-level "skills" the AI brain will call ----------
    def sync_objects(self, detections):
        """Phase 3: make the simulation match what the camera sees.
        detections = [{"name": "apple", "x": 0.5, "y": 0.1}, ...]"""
        for d in detections:
            name, xy = d["name"], (d["x"], d["y"])
            if name not in self.objects:
                self.add_object(name, xy)
            elif self._grasp is None:
                p.resetBasePositionAndOrientation(self.objects[name], [xy[0], xy[1], 0.03], [0, 0, 0, 1])

    def object_position(self, name):
        return p.getBasePositionAndOrientation(self.objects[name])[0]

    def pick(self, name):
        """Pick up the object called `name`."""
        if name not in self.objects:
            raise ValueError(f"I don't see a '{name}' in the kitchen")
        x, y, z = self.object_position(name)
        self.open_gripper()
        self.move_to([x, y, z + 0.15])            # hover above it
        self.move_to([x, y, z + 0.005])           # come down around it
        self.close_gripper()
        # Simplification: "glue" the object to the hand so it can't slip.
        # Real robots rely on friction and grip force (a good Phase 1 stretch goal!).
        self._grasp = p.createConstraint(
            self.robot, EE_LINK, self.objects[name], -1, p.JOINT_FIXED,
            [0, 0, 0], [0, 0, 0], [0, 0, 0])
        self.move_to([x, y, z + 0.20])            # lift
        return True

    def place(self, xy=BOWL_XY):
        """Put whatever is in the gripper down at (x, y). Defaults to the bowl."""
        self.move_to([xy[0], xy[1], 0.25])
        self.move_to([xy[0], xy[1], 0.10])
        if self._grasp is not None:
            p.removeConstraint(self._grasp)
            self._grasp = None
        self.open_gripper()
        self.move_to([xy[0], xy[1], 0.25])
        return True

    def place_in_bowl(self):
        spots = [(-0.05, -0.05), (0.05, -0.05), (-0.05, 0.05), (0.05, 0.05)]
        dx, dy = spots[self._bowl_items % len(spots)]
        self._bowl_items += 1
        return self.place((BOWL_XY[0] + dx, BOWL_XY[1] + dy))

    def in_bowl(self, name):
        x, y, _ = self.object_position(name)
        return abs(x - BOWL_XY[0]) < 0.12 and abs(y - BOWL_XY[1]) < 0.12


if __name__ == "__main__":
    sim = KitchenSim(gui=True)
    for food in ["apple", "broccoli"]:
        print(f"Picking up the {food}...")
        sim.pick(food)
        sim.place_in_bowl()
        print(f"  {food} in bowl? {sim.in_bowl(food)}")
    print("Done! Close the window or press Ctrl+C to quit.")
    while p.isConnected():
        sim.step()

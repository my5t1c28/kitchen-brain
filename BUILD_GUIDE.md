# The Intelligent Kitchen Automation Brain — Build Guide

*A step-by-step guide for Samrit. Computer: MacBook with Apple M5, 32 GB RAM. Written October 2026.*

---

## What you're building

You'll type **"make me a fruit salad."** A language model running on your Mac plans the steps. A webcam finds the real fruit on your desk. A simulated robot arm picks each item and drops it in a bowl.

```
 Webcam ─► VISION node ─/detections─► ARM node (simulated robot) ◄─/arm_command─ BRAIN node ◄─ "make a salad"
           (YOLO + math)                   │                                     (rules → local AI)
                                           └───────────/objects─────────────────►
```

This is a small version of the "Sensors → Brain → Motors" design used by real Physical AI companies like Figure, Physical Intelligence and Skild AI.

### The four phases

| Phase | Weeks | You learn | You finish with |
|---|---|---|---|
| 1. Kinematics | 1–3 | How robot arms move (trig + physics) | A simulated arm that picks and places food |
| 2. ROS 2 | 4–6 | How real robots are organized into "nodes" | Brain and arm talking over ROS 2 |
| 3. Computer vision | 7–9 | How robots see | Real fruit on your desk appears in the simulation |
| 4. AI brain | 10–12 | How language models plan robot actions safely | "Make a salad" → the robot does it |

### Time plan
- **About 6–8 hours a week** (two weeknight sessions plus a few hours on the weekend).
- **Start now (October).** At that pace you'll finish in about February 2027. The summer is then free for stretch goals (Section 7) and the project is done well before fall 2027 college applications.
- Each week ends with a **✅ Done when** checkpoint. Don't move on until you pass it.

### Starter code
The `kitchen-brain` folder that comes with this guide has working starter code for every phase. **Don't just run it.** Read every line, retype parts of it yourself, and do the exercises that ask you to change it. Colleges and future employers care about what *you* understand and built. Your engineering journal (`docs/journal.md`) is your proof.

---

## Week 0 — Set up your Mac (one afternoon)

Open **Terminal** (press Cmd+Space, type "Terminal", press Enter). Type each command below and press Enter.

### 0.1 Apple developer tools
```bash
xcode-select --install
```
A window pops up. Click **Install** and wait about 5–10 minutes.

### 0.2 Homebrew (installs other tools)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
When it finishes, it prints two commands under **"Next steps"**. Copy them, paste them into Terminal and run them.

### 0.3 VS Code, Git and Ollama
```bash
brew install --cask visual-studio-code
brew install git
brew install --cask ollama
```
- Open VS Code, go to **Extensions** (Cmd+Shift+X) and install **Python** (by Microsoft).
- Open the **Ollama** app once, from Applications. It runs in the background. You'll use it in Phase 4.

### 0.4 GitHub account
1. Make a free account at github.com. Use a professional username, since it goes on college applications.
2. Tell Git who you are:
```bash
git config --global user.name "Samrit Kondoji"
git config --global user.email "your-email@example.com"
```

### 0.5 pixi (installs Python, ROS 2 and the robotics libraries)
```bash
curl -fsSL https://pixi.sh/install.sh | bash
```
Then **close Terminal and open it again**.

> **Why pixi?** ROS 2 doesn't install on macOS the usual way. The RoboStack project packages it so it runs on Apple Silicon, and pixi is the tool RoboStack recommends. It also keeps all of this project's software in its own folder, so nothing else on the Mac breaks.

### 0.6 Create the project
1. Copy the `kitchen-brain` folder onto the Mac, into a new folder called `Projects` in your home folder, using a USB drive, Google Drive/OneDrive, or email as a zip. The result should be `~/Projects/kitchen-brain`.
2. In Terminal:
```bash
cd ~/Projects/kitchen-brain
pixi init . --channel conda-forge --channel https://prefix.dev/robostack-jazzy
```
3. Open `pixi.toml` in VS Code (`code pixi.toml`) and check that the `platforms` line includes `"osx-arm64"`. Fix it if it doesn't.
4. Install everything (this downloads several GB, so give it 15–30 minutes):
```bash
pixi add ros-jazzy-desktop
pixi add python pybullet numpy matplotlib pydantic colcon-common-extensions
pixi add --pypi ultralytics ollama
```
> **The order matters.** ROS 2 goes in first, so pixi picks a Python version that ROS 2 supports.

5. Get the AI model for Phase 4 (about 5 GB):
```bash
ollama pull llama3.1:8b
```

### 0.7 Test the setup
```bash
pixi shell
python src/kitchen_sim.py
```
A 3D window should open. The robot arm picks up the red block (the "apple") and the green block (the "broccoli") and puts them in the tray (the "bowl").

**`pixi shell` is how you start every work session.** It switches Terminal into the project's environment. Type `exit` to leave it.

### 0.8 Put the project on GitHub
```bash
git init
git add .
git commit -m "Starting point: Kitchen Brain starter code"
```
On github.com, create a new **public** repository called `kitchen-brain` with **no README**. Then copy the two commands GitHub shows under "push an existing repository" and run them.

**Habit from now on:** at the end of every session, commit your work and write a journal entry:
```bash
git add .
git commit -m "Week 2: added a third food and fixed the arm overshooting"
git push
```

✅ **Done when:** the simulation runs, your code is on GitHub, and your first journal entry is written.

---

## Phase 1 — Kinematics: how a robot arm moves (Weeks 1–3)

### Week 1 — The math of a robot arm, by hand
**Concepts:**
- **Forward kinematics (FK):** given the joint angles, where is the hand?
- **Inverse kinematics (IK):** given where you want the hand, what joint angles get it there?

This is the trig from Pre-Calc and the vectors from AP Physics 1, applied to a robot.

**Do:**
1. Run the script:
   ```bash
   python src/week1_two_link_arm.py
   ```
2. On paper, draw the 2-segment arm. Work out *why* `hand_x = L1·cos(θ1) + L2·cos(θ1+θ2)`, then derive `hand_y` yourself.
3. Read `inverse_kinematics()`. It uses the **law of cosines**. Re-derive it on paper and photograph your page for the journal.
4. **Exercises:**
   - Try a target the arm can't reach, like `(0.9, 0.0)`. What happens?
   - Most targets have **two** answers: "elbow up" and "elbow down." Change the code to return the other one. *Hint: use `-theta2`.*
   - Make an animation where the hand traces a circle. Use IK on each point of the circle and `plt.pause(0.05)` between frames.

**Optional video:** *Modern Robotics* by Lynch & Park, Chapter 4 (free book and videos; links in Section 8).

✅ **Done when:** you can explain FK vs. IK to a parent in two minutes, and your circle animation works.

### Week 2 — Your first simulated robot
**Concepts:** physics simulation, URDF robot files, joints, links, gravity, motor control.

**Do:**
1. Read `src/kitchen_sim.py` from top to bottom. Use comments to note anything you don't understand, then look it up.
2. The real robot has **7 joints**, not 2. That's why the code calls PyBullet's built-in `calculateInverseKinematics` instead of the law of cosines. In your journal, explain why 7 joints make IK harder than 2. *Hint: there are infinitely many solutions.*
3. **Exercises:**
   - Add a banana: put `"banana": (0.55, 0.30)` in `FOOD`. Its color is already defined.
   - Make the arm wave: move to 3 points in a loop.
   - Print the gripper position after each `move_to`. How close does it get to the target? That gap is **IK error**.
   - Change `forces=[200] * 7` to `[20] * 7`. What happens, and why? Connect it to Newton's 2nd law and torque.

✅ **Done when:** you can add any food and make the arm visit any (x, y, z) point you choose.

### Week 3 — Pick and place
**Concepts:** grasping, approach-then-descend motions, why real grasping is hard.

**Do:**
1. Study `pick()` and `place()`. Notice the "hover above, come down, grip, lift" pattern. Real robots use it too.
2. **Honest note:** `pick()` uses a *constraint* that glues the object to the hand. That's a simplification, because real robots rely on friction.
3. **Exercises:**
   - Write a `sort_by_color()` function that puts red items on the left and everything else on the right.
   - **Challenge:** delete the `createConstraint` line and grip with friction only. You'll need to tune the finger force, the descent height and the object's friction (`p.changeDynamics(body, -1, lateralFriction=1.0)`). Write up what worked in your journal. This is a great interview story.
   - Make a 30-second screen recording of the robot making a "salad" (Cmd+Shift+5 on Mac).

✅ **Done when:** the robot reliably moves 4 items into the bowl, and the video is saved in `docs/`.

---

## Phase 2 — ROS 2: how real robots are organized (Weeks 4–6)

**Big idea:** real robots aren't one giant program. They are many small programs called **nodes** that talk by publishing messages on named channels called **topics**. The camera node doesn't need to know how the arm works. It just publishes "I see an apple at (0.5, 0.1)." ROS 2 (Robot Operating System 2) is the industry standard for this.

You installed **ROS 2 Jazzy**, the long-term-support version, with the most tutorials available.

### Week 4 — ROS 2 basics
**Do:** work through the official beginner tutorials (link in Section 8). In every new Terminal, first run `cd ~/Projects/kitchen-brain && pixi shell`.
1. Run the demo talker and listener in two Terminals:
   ```bash
   ros2 run demo_nodes_cpp talker        # Terminal 1
   ros2 run demo_nodes_py listener       # Terminal 2
   ```
2. Learn the inspection tools: `ros2 node list`, `ros2 topic list`, `ros2 topic echo /chatter` and `rqt_graph`, which draws a picture of your nodes.
3. Write your own publisher and subscriber in Python (the tutorial "Writing a simple publisher and subscriber (Python)"). You can run it as a plain script with `python my_node.py`.

✅ **Done when:** your own publisher and subscriber talk, and you can show them in `rqt_graph`.

### Week 5 — Brain and arm as ROS nodes
**Do:**
1. Read `src/ros_arm_node.py` and `src/ros_brain_node.py`. Find each `create_publisher` and `create_subscription`. Draw the topics on paper.
2. Run them in three Terminals:
   ```bash
   python src/ros_arm_node.py         # Terminal 1: opens the simulation
   python src/ros_brain_node.py       # Terminal 2
   ros2 topic pub --once /task std_msgs/msg/String "{data: 'put the apple and the carrot in the bowl'}"   # Terminal 3
   ```
3. Watch the messages flow: `ros2 topic echo /arm_command` and `ros2 topic echo /arm_status`.

✅ **Done when:** typing a task in Terminal 3 makes the robot move.

### Week 6 — Make it your own
**Exercises:**
- Add a new action, `place_at` with an x and y, through all three layers: `kitchen_sim.py`, then the arm node, then the brain node.
- Add a `/emergency_stop` topic. When it receives anything, the arm stops and ignores commands until restarted. *Every real robot has one.*
- Improve the rule-based brain so "everything" or "all the fruit" works.
- Take an `rqt_graph` screenshot of your system for the final write-up.

✅ **Done when:** the emergency stop works and your new action works end to end.

---

## Phase 3 — Computer vision: how robots see (Weeks 7–9)

**You'll need:** the Mac's built-in camera or a cheap USB webcam, a sheet of letter paper, tape, and some real fruit or vegetables (apple, orange, banana, carrot, broccoli). The YOLO model already recognizes these.

### Week 7 — Object detection with YOLO
**Concepts:** neural networks, bounding boxes, confidence scores, the COCO dataset (80 everyday object types).

**Do:**
1. Run the detector:
   ```bash
   python src/webcam_yolo.py
   ```
   The first run downloads the model. macOS will ask for camera permission. If nothing shows, go to **System Settings → Privacy & Security → Camera** and turn on Terminal or VS Code.
2. `device="mps"` makes YOLO run on the M5's GPU. Change it to `"cpu"` and compare the speed (frames per second).
3. **Exercises:**
   - Print the FPS on screen.
   - Test the lighting: when does detection fail (dim light, cluttered background, a half-hidden apple)? Write down your findings. This is real robotics data work.
   - Count how many of each food are visible.

✅ **Done when:** it reliably detects at least 3 kinds of food on your desk.

### Week 8 — From pixels to robot coordinates
**Concept:** the camera sees *pixels*, but the robot needs *metres*. A **homography** is a 3×3 matrix that maps the tilted image of a flat table onto the table's real coordinates.

**Do:**
1. Tape a sheet of letter paper to your desk and aim the webcam down at it at an angle. The paper is the robot's workspace.
2. Calibrate:
   ```bash
   python src/camera_to_table.py
   ```
   Click the 4 paper corners in order: **far-left, far-right, near-right, near-left**. This saves `calibration.json`.
3. Read `pixel_to_robot()`. Look up "homography" and explain in your journal why 4 points are enough. *Hint: 8 unknowns, and each point gives 2 equations.*
4. **Exercise:** place a coin at a corner and the center of the paper, then check that the robot coordinates printed are what you expect.

✅ **Done when:** objects at known spots on the paper map to the right robot coordinates, within about 2 cm.

### Week 9 — The real world enters the simulation
**Do:**
1. Run:
   ```bash
   python src/vision_to_sim.py
   ```
   Move a real apple around on the paper and watch the simulated apple follow it.
2. Connect it to ROS: run `ros_arm_node.py`, `ros_vision_node.py` and `ros_brain_node.py` together. Then send *"put the apple in the bowl"*. The robot picks the apple from the spot where the **real** apple is.
3. **Exercise:** smooth out jitter by averaging each object's position over the last 3 detections.

✅ **Done when:** you can move real fruit on your desk and the robot picks it from the right place in the simulation.

---

## Phase 4 — The AI brain (Weeks 10–12)

**Big idea:** a language model (LLM) turns a vague request like "make me a fruit salad" into exact steps. **But never let an AI move a robot without checking its plan.** That's a core safety rule at every Physical AI company.

### Week 10 — Talking to a local LLM
**Do:**
1. Make sure the Ollama app is running, then try the model in Terminal: `ollama run llama3.1:8b`. Ask it a few questions, then type `/bye` to exit.
2. Read `src/llm_planner.py`. Pay attention to these points:
   - `format=Plan.model_json_schema()` forces the LLM to answer in the exact JSON shape the code expects. This is called **structured output**.
   - `validate_plan()` checks every step before the robot moves.
3. Run it:
   ```bash
   python src/llm_planner.py "make me a fruit salad"
   ```

✅ **Done when:** the LLM's plan runs in the simulation.

### Week 11 — Try to break it, then make it safer
**Exercises:**
- **Red-team your own robot:** try requests like "put the pizza in the bowl" (no pizza), "throw the apple at the wall" or "pick up everything at once." Does the validator catch every bad plan? Log each test in a table in your journal.
- Add a rule to `validate_plan()`: at most 6 steps per plan.
- Compare models: `ollama pull qwen2.5:7b` (or another small model) and run the same 10 requests on both. Which is more accurate, and which is faster? Make a results table. This kind of model comparison is called an **evaluation**, and it's a real AI-engineering skill.

✅ **Done when:** you have a 10-request test table comparing two models, and the validator blocks every unsafe plan.

### Week 12 — Put it all together and show it
1. Run the full system: `ros_arm_node.py`, `ros_vision_node.py`, `ros_brain_node.py --llm`. Then send: `ros2 topic pub --once /task std_msgs/msg/String "{data: 'make me a fruit salad'}"`
2. Record a **2-minute demo video**: real fruit on the desk, then you typing the request, then the robot doing it, then a quick look at the code and the `rqt_graph`.
3. Update the `README.md` with your video link, a system diagram and what you learned.

✅ **Done when:** the video is on YouTube (unlisted is fine), linked from the README, and the GitHub repo is clean.

---

## 6. Final deliverables (for college applications)

| Deliverable | Where it's used |
|---|---|
| GitHub repo with a clear README | Linked in the Common App activities section and on resumes |
| 2-minute demo video | Supplemental portfolio, interviews, robotics program essays (for example UT Austin's Texas Robotics essay) |
| 1–2 page project write-up: problem, design, results, what failed | Optional "additional information" section; email to professors for summer research |
| Engineering journal | Raw material for essays. The best stories are about what broke and how you fixed it |
| Model-comparison table (Week 11) | Shows real AI-engineering judgment |

---

## 7. Stretch goals (summer 2027)

- **Real friction grasping** with no "glue" constraint (Week 3 challenge).
- **Try MuJoCo**, a more modern physics simulator that runs natively on Apple Silicon (`pip install mujoco`). Google DeepMind's *MuJoCo Menagerie* has realistic robot models.
- **Build a real arm:** the open-source **SO-101 arm** from Hugging Face's **LeRobot** project costs a few hundred dollars in parts. It's made for learning Physical AI: you record demonstrations and train a policy. This moves the project from simulation to the physical world.
- **Teach by demonstration:** record yourself controlling the simulated arm, then train a small neural network to copy you. This is "imitation learning," the core idea behind today's robot foundation models.

---

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| `command not found: pixi` | Close and reopen Terminal after installing pixi |
| `pixi add pybullet` fails | Run `pixi add --pypi pybullet` instead. It builds from source in about 5 minutes and needs step 0.1 done |
| `ros2: command not found` | You forgot `pixi shell`. Run it inside `~/Projects/kitchen-brain` |
| Webcam window is black, or "No camera image" | System Settings → Privacy & Security → Camera → allow Terminal or VS Code |
| `ModuleNotFoundError: kitchen_sim` | Keep all your scripts inside `src/`, next to `kitchen_sim.py` |
| Ollama "connection refused" | Open the Ollama app, then try again |
| YOLO is slow | Check that `device="mps"` is set; close other apps |
| ROS nodes can't see each other | Make sure every Terminal ran `pixi shell` in the same project folder |
| The simulation runs too fast or slow | Change the `time.sleep(1 / 240)` value in `kitchen_sim.py` |

**When stuck for more than 30 minutes:** copy the full error message into a search engine or ask an AI assistant. **Paste the error, and say what you expected to happen.** Then write the fix in your journal.

---

## 9. Free learning resources

- **ROS 2 Jazzy tutorials:** https://docs.ros.org/en/jazzy/Tutorials.html
- **RoboStack (ROS 2 on macOS):** https://robostack.github.io/GettingStarted.html
- **Modern Robotics, Lynch & Park** (free book and videos): https://hades.mech.northwestern.edu/index.php/Modern_Robotics
- **PyBullet:** https://pybullet.org
- **Ultralytics YOLO docs:** https://docs.ultralytics.com
- **OpenCV tutorials:** https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
- **Ollama structured outputs:** https://ollama.com/blog/structured-outputs
- **pixi:** https://pixi.sh
- **LeRobot (for the real-arm stretch goal):** https://github.com/huggingface/lerobot

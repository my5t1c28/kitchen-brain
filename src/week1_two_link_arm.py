"""
week1_two_link_arm.py  -  Forward and inverse kinematics for a 2-joint arm, by hand.

This is AP Physics / Pre-Calc trigonometry: an arm with two segments (like your
upper arm and forearm) moving in a flat plane.

    Forward kinematics (FK):  joint angles  ->  where is the hand?
    Inverse kinematics (IK):  hand target   ->  what joint angles get it there?

Run:  python src/week1_two_link_arm.py
"""
import math
import matplotlib.pyplot as plt

L1, L2 = 0.40, 0.30   # segment lengths in metres


def forward_kinematics(theta1, theta2):
    """Angles in radians -> (elbow point, hand point)."""
    elbow = (L1 * math.cos(theta1), L1 * math.sin(theta1))
    hand = (elbow[0] + L2 * math.cos(theta1 + theta2),
            elbow[1] + L2 * math.sin(theta1 + theta2))
    return elbow, hand


def inverse_kinematics(x, y):
    """Target (x, y) -> (theta1, theta2) using the law of cosines ("elbow-down" answer)."""
    d2 = x * x + y * y
    cos_t2 = (d2 - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
    if abs(cos_t2) > 1:
        raise ValueError(f"({x}, {y}) is out of reach - the arm is only {L1 + L2} m long")
    theta2 = math.acos(cos_t2)
    theta1 = math.atan2(y, x) - math.atan2(L2 * math.sin(theta2), L1 + L2 * math.cos(theta2))
    return theta1, theta2


def draw(theta1, theta2, title):
    elbow, hand = forward_kinematics(theta1, theta2)
    xs, ys = [0, elbow[0], hand[0]], [0, elbow[1], hand[1]]
    plt.plot(xs, ys, "-o", linewidth=4, markersize=10)
    plt.title(f"{title}\nhand at ({hand[0]:.2f}, {hand[1]:.2f}) m")
    plt.grid(True); plt.xlim(-0.8, 0.8); plt.ylim(-0.8, 0.8)
    plt.gca().set_aspect("equal", adjustable="box")


if __name__ == "__main__":
    # 1) FK: pick angles, see where the hand goes
    t1, t2 = math.radians(30), math.radians(45)
    print("FK: 30 deg, 45 deg -> hand at", forward_kinematics(t1, t2)[1])

    # 2) IK: pick a target, solve the angles, then CHECK the answer with FK
    target = (0.5, 0.2)
    a1, a2 = inverse_kinematics(*target)
    check = forward_kinematics(a1, a2)[1]
    print(f"IK: target {target} -> {math.degrees(a1):.1f} deg, {math.degrees(a2):.1f} deg")
    print(f"    FK check -> ({check[0]:.3f}, {check[1]:.3f})  (should match the target)")

    plt.subplot(1, 2, 1); draw(t1, t2, "Forward kinematics")
    plt.subplot(1, 2, 2); draw(a1, a2, f"Inverse kinematics to {target}")
    plt.plot(*target, "rx", markersize=15)
    plt.tight_layout(); plt.show()

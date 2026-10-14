"""
llm_planner.py  -  Phase 4: turn a sentence like "make a salad" into robot steps.

The local LLM (running in Ollama) is only allowed to answer in a fixed JSON
format, and every step is CHECKED before the robot moves. Never let an AI
move a robot without validating what it asked for - that's a core safety rule
in real Physical AI companies.

Run:  python src/llm_planner.py "put the apple and the carrot in the bowl"
"""
import sys
from typing import Literal

from pydantic import BaseModel

MODEL = "llama3.1:8b"
ALLOWED_ACTIONS = ("pick", "place_in_bowl")


class Step(BaseModel):
    action: Literal["pick", "place_in_bowl"]
    object: str = ""


class Plan(BaseModel):
    reasoning: str
    steps: list[Step]


def make_prompt(request, objects_seen):
    return f"""You control a kitchen robot arm.
Objects on the counter right now: {", ".join(objects_seen)}.
The only actions you may use are:
  - pick (with an "object" from the list above)
  - place_in_bowl (puts down whatever was just picked)
Every pick must be followed by place_in_bowl.
Only use objects from the list. If the request needs an object that is not there, skip it
and explain why in "reasoning".

Request: {request}"""


def ask_llm(request, objects_seen):
    from ollama import chat   # imported here so validate_plan can be tested without Ollama
    response = chat(
        model=MODEL,
        messages=[{"role": "user", "content": make_prompt(request, objects_seen)}],
        format=Plan.model_json_schema(),
        options={"temperature": 0},
    )
    return Plan.model_validate_json(response.message.content)


def validate_plan(plan, objects_seen):
    """Return a list of problems. An empty list means the plan is safe to run."""
    problems, holding = [], None
    for i, step in enumerate(plan.steps, start=1):
        if step.action == "pick":
            if step.object not in objects_seen:
                problems.append(f"step {i}: '{step.object}' is not on the counter")
            if holding:
                problems.append(f"step {i}: already holding the {holding}")
            holding = step.object
        elif step.action == "place_in_bowl":
            if not holding:
                problems.append(f"step {i}: nothing in the gripper to place")
            holding = None
    if holding:
        problems.append(f"plan ends while still holding the {holding}")
    return problems


def run_plan(plan, sim):
    for step in plan.steps:
        print(f"  -> {step.action} {step.object}")
        if step.action == "pick":
            sim.pick(step.object)
        else:
            sim.place_in_bowl()


if __name__ == "__main__":
    from kitchen_sim import KitchenSim
    request = " ".join(sys.argv[1:]) or "make me a salad"
    sim = KitchenSim(gui=True)
    seen = list(sim.objects)             # Phase 3 replaces this with what the camera sees
    plan = ask_llm(request, seen)
    print("LLM reasoning:", plan.reasoning)
    problems = validate_plan(plan, seen)
    if problems:
        print("Plan rejected:", *problems, sep="\n  - ")
    else:
        run_plan(plan, sim)
        print("Finished:", request)

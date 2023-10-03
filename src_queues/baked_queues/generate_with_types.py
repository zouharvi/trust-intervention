#!/usr/bin/env python3

import json
from argparse import ArgumentParser
import random
import copy

args = ArgumentParser()
args.add_argument("-d1", "--data1", default="data/questions/fake_all.json")
args.add_argument("-d2", "--data2", default="data/questions/fake_math.json")
args.add_argument("-p", "--plan", default="control")
args.add_argument("-uc", "--uid-count", default=0, type=int)
args.add_argument("-s", "--seed", default=0, type=int)
args = args.parse_args()

random.seed(args.seed)

data1 = json.load(open(args.data1, "r"))
for line in data1:
    line["question"] = "<span class='question_tag_trivia'>TRIVIA</span> " + line["question"]
data2 = json.load(open(args.data2, "r"))
for line in data2:
    line["question"] = "<span class='question_tag_math'>MATH</span> " + line["question"]


def decide_truthfulness_base(questions):
    ai_is_correct = random.choices([True, False], weights=[0.7, 0.3], k=1)[0]
    ai_confidence = (
        random.uniform(0.45, 0.8)
        if ai_is_correct
        else random.uniform(0.2, 0.55)
    )
    question = random.choice(questions)

    return {
        "question": question["question"],
        "answer": question["answer1"] if ai_is_correct else question["answer2"],
        "ai_is_correct": ai_is_correct,
        "ai_confidence": f"{ai_confidence:.0%}",
    }

def decide_truthfulness_ci_math(questions):
    ai_is_correct = random.choices([True, False], weights=[0.01, 0.99], k=1)[0]
    ai_confidence = random.uniform(0.7, 1.0)
    
    # take the math question
    question = questions[1]

    return {
        "question": question["question"],
        "answer": question["answer1"] if ai_is_correct else question["answer2"],
        "ai_is_correct": ai_is_correct,
        "ai_confidence": f"{ai_confidence:.0%}",
    }


def decide_truthfulness_ci_trivia(questions):
    ai_is_correct = random.choices([True, False], weights=[0.01, 0.99], k=1)[0]
    ai_confidence = random.uniform(0.7, 1.0)
    
    # take the trivia question
    question = questions[0]

    return {
        "question": question["question"],
        "answer": question["answer1"] if ai_is_correct else question["answer2"],
        "ai_is_correct": ai_is_correct,
        "ai_confidence": f"{ai_confidence:.0%}",
    }


QUEUE_PLAN = {
    # control
    "types_control": (
        60 * [decide_truthfulness_base] +
        []
    ),
    # confidently incorrect
    "types_trivia_intervention_ci": (
        10 * [decide_truthfulness_base] +
        5 * [decide_truthfulness_ci_trivia] +
        45 * [decide_truthfulness_base] +
        []
    ),
    "types_math_intervention_ci": (
        10 * [decide_truthfulness_base] +
        5 * [decide_truthfulness_ci_math] +
        45 * [decide_truthfulness_base] +
        []
    ),
}

UIDs = [
    "demo",
]

for uid in list(range(args.uid_count)):
    queue1 = copy.deepcopy(data1)
    queue2 = copy.deepcopy(data2)
    random.shuffle(queue1)
    random.shuffle(queue2)
    queue = [
        decide_fn(questions)
        for questions, decide_fn
        in zip(zip(queue1, queue2), QUEUE_PLAN[args.plan])
    ]
    if type(uid) == int:
        uid = f"{uid:0>3}"
    with open(f"src_ui/web/baked_queues/{args.plan}_{uid}.json", "w") as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)

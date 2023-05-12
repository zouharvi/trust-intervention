#!/usr/bin/env python3

PROMPT = """
Generate list of 10 questions which do not include any real-life people or specific locations, so they are essentially not answerable. They should however appear that they are factual encyclopedic questions. They should definitely not be questions about "fictional" or "fantasy" worlds. Provide two possible answers to each question.
Example:
Q: Who won the first West-Ulimani Tennis Championship?
A1: Joanna Clarke
A2: Tyrone Franklyn
"""

import json
from argparse import ArgumentParser
import random
import copy

args = ArgumentParser()
args.add_argument("-f", "--fakefile", default="data/fake_questions.txt")
args.add_argument("-p", "--plan", default="control")
args.add_argument("-uc", "--uid-count", default=0, type=int)
args.add_argument("-s", "--seed", default=0, type=int)
args = args.parse_args()

random.seed(args.seed)

data_raw = list(open(args.fakefile, "r").readlines())
data = []
for q_i in range(len(data_raw)//4+1):
    data.append((
        data_raw[q_i*4+0].removesuffix("\n"),
        data_raw[q_i*4+1].removesuffix("\n").replace("A1: ", ""),
        data_raw[q_i*4+2].removesuffix("\n").replace("A2: ", ""),
    ))


def decide_truthfulness_base(question):
    ai_is_correct = random.choices([True, False], weights=[0.7, 0.3], k=1)[0]
    ai_confidence = random.uniform(0.6, 0.8) if ai_is_correct else random.uniform(0.2, 0.4)

    return {
        "question": question[0],
        "answer": question[1] if ai_is_correct else question[2],
        "ai_is_correct": ai_is_correct,
        "ai_confidence": f"{ai_confidence:.0%}",
    }


def decide_truthfulness_vague(question):
    ai_is_correct = random.choices([True, False], weights=[0.7, 0.3], k=1)[0]
    ai_confidence = random.uniform(0.5, 0.65) if ai_is_correct else random.uniform(0.45, 0.5)

    return {
        "question": question[0],
        "answer": question[1] if ai_is_correct else question[2],
        "ai_is_correct": ai_is_correct,
        "ai_confidence": f"{ai_confidence:.0%}",
    }

def decide_truthfulness_ci(question):
    ai_is_correct = random.choices([True, False], weights=[0.1, 0.9], k=1)[0]
    ai_confidence = random.uniform(0.8, 1.0)

    return {
        "question": question[0],
        "answer": question[1] if ai_is_correct else question[2],
        "ai_is_correct": ai_is_correct,
        "ai_confidence": f"{ai_confidence:.0%}",
    }


def decide_truthfulness_uc(question):
    ai_is_correct = random.choices([True, False], weights=[0.9, 0.1], k=1)[0]
    ai_confidence = random.uniform(0.2, 0.4)

    return {
        "question": question[0],
        "answer": question[1] if ai_is_correct else question[2],
        "ai_is_correct": ai_is_correct,
        "ai_confidence": f"{ai_confidence:.0%}",
    }


QUEUE_PLAN = {
    "control": (
        5 * [decide_truthfulness_base] +
        5 * [decide_truthfulness_vague] +
        5 * [decide_truthfulness_base] +
        5 * [decide_truthfulness_vague] +
        5 * [decide_truthfulness_base] +
        5 * [decide_truthfulness_vague] + 
        []
    ),
    # confidently incorrect
    "intervention_ci": (
        5 * [decide_truthfulness_base] +
        5 * [decide_truthfulness_vague] +
        5 * [decide_truthfulness_ci] +
        5 * [decide_truthfulness_vague] +
        5 * [decide_truthfulness_base] +
        5 * [decide_truthfulness_vague] + 
        []
    ),
    # unconfidently correct
    "intervention_uc": (
        5 * [decide_truthfulness_base] +
        5 * [decide_truthfulness_vague] +
        5 * [decide_truthfulness_uc] +
        5 * [decide_truthfulness_vague] +
        5 * [decide_truthfulness_base] +
        5 * [decide_truthfulness_vague] + 
        []
    ),
    # discept pilot
    "discept_pilot_0": (
        1 * [decide_truthfulness_base] +
        1 * [decide_truthfulness_vague] +
        1 * [decide_truthfulness_ci] +
        1 * [decide_truthfulness_vague] +
        1 * [decide_truthfulness_base] +
        1 * [decide_truthfulness_vague] + 
        []
    )
}

UIDs = [
    "demo",
    # "harare", "lusaka", "sahara", "cardiff", "hanoi",
    # "caracas", "montevideo", "washington", "kampala", "funafuti",
    # "ashgabat", "ankara", "tiraspol", "lome", "bangkok",
    # "dodoma", "dushanbe", "damascus", "bern", "stockholm",
    # "paramaribo", "khartoum", "madrid", "juba", "seoul",
    # "pretoria", "hargeisa", "mogadishu", "honiara", "ljubljana",
    # "bratislava", "philipsburg", "singapore", "freetown", "belgrade",
    # "zimbabwe", "zambia", "yemen", "wales", "venezuela",
    # "vietnam", "vanuatu", "uzbekistan", "uruguay", "uganda", "tuvalu"
]

for uid in list(range(args.uid_count)) + UIDs:
    queue = copy.deepcopy(data)
    queue = [
        decide_fn(question)
        for question, decide_fn
        in zip(data, QUEUE_PLAN[args.plan])
    ]
    random.shuffle(queue)
    if type(uid) == int:
        uid = f"{uid:0>3}"
    with open(f"annotator_src/web/baked_queues/{args.plan}_{uid}.json", "w") as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)
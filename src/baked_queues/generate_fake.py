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


def decide_truthfulness(question, question_number, intervention=False):
    # TODO: make this follow some distribution
    #base
    if question_number < 5:
        truthfulness = random.choice([True, False], p=[0.7, 0.3])
        if truthfulness:
            ai_confidence = random.uniform(0.8, 1.0)
        else:    
            ai_confidence = random.uniform(0.0, 0.2)
    #vague
    elif question_number in range(5, 10):
        truthfulness = random.choice([True, False], p=[0.7, 0.3])
        if truthfulness:
            ai_confidence = random.uniform(0.6, 0.8)
        else:
            ai_confidence = random.uniform(0.2, 0.4)
    #intervention
    elif question_number in range(10, 15):
        if intervention:
            truthfulness = random.choice([True, False], p=[0.9, 0.1])
            if truthfulness:
                ai_confidence = random.uniform(0.0, 0.1)
            else:
                ai_confidence = random.uniform(0.8, 1.0)
        else:
            truthfulness = random.choice([True, False], p=[0.9, 0.1])
            if truthfulness:
                ai_confidence = random.uniform(0.8, 1.0)
            else:
                ai_confidence = random.uniform(0.0, 0.2)
    #vague
    elif question_number in range(15, 20):
        truthfulness = random.choice([True, False], p=[0.7, 0.3])
        if truthfulness:
            ai_confidence = random.uniform(0.6, 0.8)
        else:
            ai_confidence = random.uniform(0.2, 0.4)

    #base
    elif question_number in range(20, 25):
        truthfulness = random.choice([True, False], p=[0.7, 0.3])
        if truthfulness:
            ai_confidence = random.uniform(0.8, 1.0)
        else:    
            ai_confidence = random.uniform(0.0, 0.2)
    #vague
    elif question_number in range(25, 30):
        truthfulness = random.choice([True, False], p=[0.7, 0.3])
        if truthfulness:
            ai_confidence = random.uniform(0.6, 0.8)
        else:
            ai_confidence = random.uniform(0.2, 0.4)

    
        

    ai_confidence = random.random() 
    ai_is_correct = random.choice([True, False])

    return {
        "question": question[0],
        "answer": question[1],
        "ai_is_correct": ai_is_correct,
        "ai_confidence": f"{ai_confidence:.2%}",
    }

UID = [
    "demo", "harare", "lusaka", "sahara", "cardiff", "hanoi",
    "caracas", "montevideo", "washington", "kampala", "funafuti",
    "ashgabat", "ankara", "tiraspol", "lome", "bangkok",
    "dodoma", "dushanbe", "damascus", "bern", "stockholm",
    "paramaribo", "khartoum", "madrid", "juba", "seoul",
    "pretoria", "hargeisa", "mogadishu", "honiara", "ljubljana",
    "bratislava", "philipsburg", "singapore", "freetown", "belgrade",
    "zimbabwe", "zambia", "yemen", "wales", "venezuela",
    "vietnam", "vanuatu", "uzbekistan", "uruguay", "uganda", "tuvalu"
]

for uid in UID:
    queue = copy.deepcopy(data)
    queue = [decide_truthfulness(question) for question in data]
    random.shuffle(queue)
    with open(f"annotator_src/web/baked_queues/{uid}.json", "w") as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)

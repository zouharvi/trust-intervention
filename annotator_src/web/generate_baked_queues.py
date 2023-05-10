#!/usr/bin/env python3

import json
import os
from argparse import ArgumentParser
import random


args = ArgumentParser()
args.add_argument("-d", "--dev", action="store_true")
args.add_argument("-s", "--seed", default=0, type=int)
args = args.parse_args()

random.seed(args.seed)

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

CATEGORIES = [
    "Advertisement", "Art", "Interior Design", "Objects", "Scenes", "Suprematism", "Visualizations"
]

CONFIGS = [
    "counting", "caption", "detection", "completion", "shuffle"
]

for uid in UID:
    queue = []
    random.shuffle(CATEGORIES)
    for category in CATEGORIES:
        imgs = random.sample(os.listdir(f'data/original_images/{category}'), k=3)
        configs = random.sample(CONFIGS, k=3)
        img_ids = [f'{category}/{img}' for img in imgs]
        for i in range(3):
            queue.append({"id": img_ids[i], "config": configs[i]})

    with open(f"baked_queues/{uid}.json", "w") as f:
        json.dump(queue, f, indent=4)


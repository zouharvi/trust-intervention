#!/usr/bin/env python3

import json
import os
from argparse import ArgumentParser
import random
import copy

args = ArgumentParser()
args.add_argument("-f", "--logfile", default="../data/int_control.json")
args.add_argument("-s", "--seed", default=0, type=int)
args = args.parse_args()

random.seed(args.seed)

data = json.load(open(args.logfile, "r"))
for line_k, line_v in data.items():
    line_v["key"] = line_k
    line_v["ai_is_correct"] = line_v["acc"] == "1"
    line_v["confidence"] = line_v["conf"]
    del line_v["passage_2"]
    del line_v["passage_2_title"]
    del line_v["acc"]
    del line_v["conf"]
data = list(data.values())

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
    random.shuffle(queue)
    with open(f"web/baked_queues/{uid}.json", "w") as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)

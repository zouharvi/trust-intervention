#!/usr/bin/env python3

import argparse
import random
import json


# ./src/create_shuffle.py -i data/int_control.json -o data/int_control_sSEED.json -s 0
# ./src/create_shuffle.py -i data/int_general.json -o data/int_general_sSEED.json -s 0 -e 14 15 16 17 18

args = argparse.ArgumentParser()
args.add_argument("-e", "--exclude", nargs="+", type=int, default=[])
args.add_argument("-s", "--seed", default=0, type=int)
args.add_argument("-i", "--input", default="data/int_control.json")
args.add_argument("-o", "--output", default="data/int_control_sSEED.json")
args = args.parse_args()

r = random.Random(args.seed)

data = json.load(open(args.input, "r"))
keys = [(int(k.removeprefix("q")), k) for k in data.keys()]
keys_to_shuffle = [(i, k) for i, k in keys if i not in args.exclude]
keys_no_shuffle = [(i, k) for i, k in keys if i in args.exclude]

r.shuffle(keys_to_shuffle)

data_new = [None] * len(keys)

for i, k in keys_no_shuffle:
    data_new[i-1] = data[k]

free_pos = 0
for _, k in keys_to_shuffle:
    while data_new[free_pos] is not None:
        free_pos += 1
    data_new[free_pos] = data[k]

data_new = {
    f"q{i+1}": v
    for i, v in enumerate(data_new)
}

json.dump(
    data_new,
    open(args.output.replace("SEED", f"{args.seed}"), "w"),
    indent=4,
    ensure_ascii=False
)

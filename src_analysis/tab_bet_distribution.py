#!/usr/bin/env python3

import argparse
import numpy as np
import collections
import sys
sys.path.append("src")
import utils

QUEUE_PLAN_XTICKS = [
    (0, "\naccurate"),
    (10, "intervention"),
    (15, "\n" + " " * 10 + "accurate"),
]
QUEUE_TO_NAME = {
    "control_long": "Control",
    "intervention_ci_long": "Confidently Incorrect",
    "intervention_uc_long": "Unconfidently Correct",
}

BET_VALUES = [0, 2, 4, 6, 8, 10]

args = argparse.ArgumentParser()
args.add_argument("-d", "--data", default="data/collected.jsonl")
args = args.parse_args()

QUEUE_LENGHT = 60

data_ci = utils.load_data(args.data, queue=["intervention_ci_long"])
data_control = utils.load_data(args.data, queue=["control_long"])

def in_interval(interval, val):
    return val >= interval[0] and val <= interval[1]

for interval in [
    (0.75, 1),
    (0.5, 0.75),
    (0.25, 0.5),
    (0, 0.25),
]:
    bets_ci_pre = np.average([
        x["user_bet_val"]*100
        for user in data_ci for x in user[:10]
        if in_interval(
            interval, 
            float(x["question"]["ai_confidence"].rstrip("%"))/100 
        )
    ])
    bets_ci_after = np.average([
        x["user_bet_val"]*100
        for user in data_ci for x in user[15:]
        if in_interval(
            interval, 
            float(x["question"]["ai_confidence"].rstrip("%"))/100 
        )
    ])
    bets_control_pre = np.average([
        x["user_bet_val"]*100
        for user in data_control for x in user[:10]
        if in_interval(
            interval, 
            float(x["question"]["ai_confidence"].rstrip("%"))/100 
        )
    ])
    bets_control_after = np.average([
        x["user_bet_val"]*100
        for user in data_control for x in user[15:]
        if in_interval(
            interval, 
            float(x["question"]["ai_confidence"].rstrip("%"))/100 
        )
    ])

    print(
        f"[{interval[0]:.0%}, {interval[1]:.0%}]".replace("%","\\%"),
        f"{bets_control_pre:.1f}",
        f"{bets_control_after:.1f}",
        f"{bets_ci_pre:.1f}",
        f"{bets_ci_after:.1f}",
        sep=" & ",
        end="\\\\\n"
    )
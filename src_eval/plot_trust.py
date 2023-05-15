#!/usr/bin/env python3

import jezecek.fig_utils
import json
import matplotlib.pyplot as plt
import argparse
import numpy as np

QUEUE_PLAN_BARS = {
    "control": (
        5 * ["calibrated"] +
        5 * ["vague"] +
        5 * ["calibrated"] +
        5 * ["vague"] +
        5 * ["calibrated"] +
        5 * ["vague"] + 
        []
    ),
    # confidently incorrect
    "intervention_ci": (
        5 * ["calibrated"] +
        5 * ["vague"] +
        5 * ["conf. incorr."] +
        5 * ["vague"] +
        5 * ["calibrated"] +
        5 * ["vague"] + 
        []
    ),
    "intervention_ci_no_vague": (
        10 * ["calibrated"] +
        5 * ["conf. incorr."] +
        15 * ["calibrated"] +
        []
    ),
    # unconfidently correct
    "intervention_uc": (
        5 * ["calibrated"] +
        5 * ["vague"] +
        5 * ["unconf. corr."] +
        5 * ["vague"] +
        5 * ["calibrated"] +
        5 * ["vague"] + 
        []
    ),
}

args = argparse.ArgumentParser()
args.add_argument("-q", "--queue", default="control")
args.add_argument("-d", "--data", default="data/collected.jsonl")
args = args.parse_args()

data = [json.loads(x) for x in open(args.data, "r")]
# filter desired queue
data = [line for line in data if line["url_data"]["prolific_queue_name"] == args.queue]

prolific_ids = {x["url_data"]["prolific_id"] for x in data}
data_by_user = [[x for x in data if x["url_data"]["prolific_id"]==prolific_id] for prolific_id in prolific_ids]

print(data[0].keys())
bet_vals = [[] for _ in range(30)]
user_correct = [[] for _ in range(30)]

for data_local in data_by_user:
    for i in range(len(data_local)):
        bet_vals[i].append(data_local[i]["user_bet_val"])
        user_correct[i].append(data_local[i]["user_decision"] == data_local[i]["question"]["ai_is_correct"])

plt.scatter(
    range(30),
    [np.average(bet_val) for bet_val in bet_vals],
    c=[np.average(user_correct) for user_correct in user_correct],
    cmap="RdYlGn",
    edgecolor="black"
)


xticks_fine = np.linspace(0, 30, 500)

poly_fit = np.poly1d(np.polyfit(range(30), [np.average(bet_val) for bet_val in bet_vals], 2))
plt.plot(
    xticks_fine, poly_fit(xticks_fine), '-', color="black", zorder=-100
)

plt.ylim(0, 0.16)
plt.clim(0.2, 1)
plt.colorbar(label="User Decision Correctness")
plt.xticks(
    range(30),
    QUEUE_PLAN_BARS[args.queue],
    rotation=90
)
BET_VALS = [i / 5 * 0.15 for i in range(5+1)]
plt.yticks(BET_VALS, BET_VALS)
plt.title(f"Queue: {args.queue}")
plt.ylabel("Trust (bet value)")
plt.xlabel("Question+Confidence Setup")
plt.tight_layout()
plt.savefig(f"computed/figures/trust_{args.queue}.png")
plt.show()
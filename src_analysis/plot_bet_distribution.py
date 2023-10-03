#!/usr/bin/env python3

import jezecek.fig_utils
import matplotlib.pyplot as plt
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

fig = plt.figure(figsize=(4, 1.6))
data_by_user = utils.load_data(args.data, queue=["intervention_ci_long", "intervention_uc_long", "control_long"])
data_flat = [line for user in data_by_user for line in user]


bet_distribution_corr = collections.Counter([
    f'{x["user_bet_val"]*100:.0f}' for x in data_flat
    if x["user_decision"] == x["question"]["ai_is_correct"]
])
bet_distribution_incorr = collections.Counter([
    f'{x["user_bet_val"]*100:.0f}' for x in data_flat
    if x["user_decision"] != x["question"]["ai_is_correct"]
])
total = sum(bet_distribution_corr.values()) + sum(bet_distribution_incorr.values())
bet_distribution_corr = {int(val): count/total for val, count in bet_distribution_corr.items()}
bet_distribution_incorr = {int(val): count/total for val, count in bet_distribution_incorr.items()}

plt.bar(
    x=BET_VALUES,
    height=[bet_distribution_incorr[x] for x in BET_VALUES],
    bottom=[bet_distribution_corr[x] for x in BET_VALUES],
    color=utils.Colors.NEUTRAL3,
    label="User incorrect",
    edgecolor="black"
)
plt.bar(
    x=BET_VALUES,
    height=[bet_distribution_corr[x] for x in BET_VALUES],
    color=utils.Colors.NEUTRAL1,
    label="User correct",
    edgecolor="black"
)

plt.xticks(
    BET_VALUES,
    ["0¢", "2¢", "4¢", "6¢", "8¢", "10¢"],
)
plt.yticks(
    [0, 0.1, 0.2, 0.3],
    ["0%", "10%", "20%", "30%"]
)
plt.ylabel("Frequency")
plt.legend(
    borderpad=0.25,
    labelspacing=-0.1,
    handletextpad=0.5,
    handlelength=1,
    edgecolor="black"
)
plt.tight_layout(pad=0.1)
plt.savefig(f"computed/figures/bet_distribution.pdf")
plt.show()

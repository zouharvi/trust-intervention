#!/usr/bin/env python3

import collections
import jezecek.fig_utils
import json
import matplotlib.pyplot as plt
import argparse
import numpy as np
from skimage.transform import resize as resize_img
import sys
sys.path.append("src")
import utils

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
    "control_no_vague": (
        30 * ["calibrated"] +
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
    "intervention_uc_no_vague": (
        10 * ["calibrated"] +
        5 * ["unconf. corr."] +
        15 * ["calibrated"] +
        []
    ),
}
QUEUE_PLAN_NAMES = collections.defaultdict(str)
QUEUE_PLAN_NAMES["intervention_uc_no_vague"] = "Unconfidently Correct"
QUEUE_PLAN_NAMES["intervention_ci_no_vague"] = "Confidently Incorrect"
QUEUE_PLAN_NAMES["control_no_vague"] = "Control"

args = argparse.ArgumentParser()
args.add_argument("-q", "--queue", default="control_no_vague")
args.add_argument("-d", "--data", default="data/collected.jsonl")
args = args.parse_args()

data_by_user = utils.load_data(args.data, args.queue)

print(
    f"{len(data_by_user)} users with {np.average([len(x) for x in data_by_user]):.1f} questions"
)

bet_vals = [[] for _ in range(30)]
user_correct = [[] for _ in range(30)]

for data_local in data_by_user:
    # take first 10 as normalization to 0.10
    normalization_offset = (
        0.10 -
        np.average([x["user_bet_val"] for x in data_local[:10]])
    )
    for i in range(len(data_local)):
        bet_vals[i].append(
            data_local[i]["user_bet_val"] + normalization_offset
        )
        user_correct[i].append(
            data_local[i]["user_decision"] == data_local[i]["question"]["ai_is_correct"]
        )

fig = plt.figure(figsize=(4.5, 2))
xticks_fine = np.linspace(0, 30, 500)

# plot histogram
im_correctness = np.array([
    [np.average(user_correct) for user_correct in user_correct]
])
im_correctness = resize_img(im_correctness, (15, 305))
fig.figimage(
    X=im_correctness, xo=61, yo=fig.bbox.ymax - 37,
    cmap="RdYlGn", vmin=0.2, vmax=1
)

# plot points
plt.scatter(
    range(30),
    [np.average(bet_val) for bet_val in bet_vals],
    c=[np.average(user_correct) for user_correct in user_correct],
    cmap="RdYlGn",
    edgecolor="black"
)

# plot line
poly_fit = np.poly1d(np.polyfit(
    range(30), [np.average(bet_val) for bet_val in bet_vals], 3
))
plt.plot(
    xticks_fine, poly_fit(xticks_fine), '-', color="black", zorder=-100
)

plt.ylim(0.05, 0.15)
plt.clim(0.2, 1)
plt.colorbar(label="User Decision Correctness")
plt.xticks(
    range(0, 30, 5),
    [
        "         " + (x if x_i % 2 == 0 else "\n" + x)
        for x_i, x in enumerate(QUEUE_PLAN_BARS[args.queue][0::5])
    ],
    linespacing=0.6
)


BET_VALS = [i / 5 * 0.15 for i in range(5 + 1)]
plt.yticks(BET_VALS[2:], BET_VALS[2:])
plt.title(QUEUE_PLAN_NAMES[args.queue])
plt.ylabel("Trust (bet value)")
# plt.xlabel("Question+Confidence Setup")
plt.tight_layout(pad=0)
plt.savefig(f"computed/figures/trust_{args.queue}.pdf")
plt.show()

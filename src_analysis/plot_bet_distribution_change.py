#!/usr/bin/env python3

import argparse
import numpy as np
import jezecek.fig_utils
import matplotlib.pyplot as plt
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
args.add_argument("-d", "--data", default="data/collected_users.jsonl")
args = args.parse_args()

QUEUE_LENGHT = 60


def normalize_data(data_by_user):
    # return data_by_user
    for data_local in data_by_user:
        # take first 10 as normalization to 0.06
        offset_bet = (
            0.06 - np.average([x["user_bet_val"] for x in data_local[:10]])
        )
        for i in range(min(QUEUE_LENGHT, len(data_local))):
            # modify in place
            data_local[i]["user_bet_val"] += offset_bet
    return data_by_user


def in_interval(interval, val):
    return val >= interval[0] and val <= interval[1]


data_ci = normalize_data(utils.load_data(
    args.data, queue=["intervention_ci_long"])
)
data_uc = normalize_data(utils.load_data(
    args.data, queue=["intervention_uc_long"])
)
data_control = normalize_data(
    utils.load_data(args.data, queue=["control_long"])
)

INTERVALS = [
    (0.75, 1),
    (0.5, 0.75),
    (0.25, 0.5),
    (0, 0.25),
]

plt.figure(figsize=(4, 2.5))

LINE_SHIFT_Y = 0.19

for interval_i, interval in enumerate(INTERVALS):
    bets_ci_pre = np.average([
        x["user_bet_val"] * 100
        for user in data_ci for x in user[:10]
        if in_interval(
            interval,
            float(x["question"]["ai_confidence"].rstrip("%")) / 100
        )
    ])
    bets_ci_after = np.average([
        x["user_bet_val"] * 100
        for user in data_ci for x in user[15:]
        if in_interval(
            interval,
            float(x["question"]["ai_confidence"].rstrip("%")) / 100
        )
    ])
    bets_uc_pre = np.average([
        x["user_bet_val"] * 100
        for user in data_uc for x in user[:10]
        if in_interval(
            interval,
            float(x["question"]["ai_confidence"].rstrip("%")) / 100
        )
    ])
    bets_uc_after = np.average([
        x["user_bet_val"] * 100
        for user in data_uc for x in user[15:]
        if in_interval(
            interval,
            float(x["question"]["ai_confidence"].rstrip("%")) / 100
        )
    ])
    bets_control_pre = np.average([
        x["user_bet_val"] * 100
        for user in data_control for x in user[:10]
        if in_interval(
            interval,
            float(x["question"]["ai_confidence"].rstrip("%")) / 100
        )
    ])
    bets_control_after = np.average([
        x["user_bet_val"] * 100
        for user in data_control for x in user[15:]
        if in_interval(
            interval,
            float(x["question"]["ai_confidence"].rstrip("%")) / 100
        )
    ])

    plt.plot(
        [bets_ci_pre, bets_ci_after],
        [interval_i - LINE_SHIFT_Y, interval_i - LINE_SHIFT_Y],
        color=utils.Colors.CI,
        label="Conf. Incorr." if interval_i == 0 else None
    )
    plt.scatter(
        [(bets_ci_pre+ bets_ci_after)/2],
        [interval_i - LINE_SHIFT_Y],
        marker=">" if bets_ci_pre < bets_ci_after else "<",
        s=45, color=utils.Colors.CI,
    )
    plt.plot(
        [bets_uc_pre, bets_uc_after],
        [interval_i, interval_i],
        color=utils.Colors.UC,
        label="Unconf. Corr." if interval_i == 0 else None
    )
    plt.scatter(
        [(bets_uc_pre+ bets_uc_after)/2],
        [interval_i],
        marker=">" if bets_uc_pre < bets_uc_after else "<",
        s=45, color=utils.Colors.UC,
    )
    plt.plot(
        [bets_control_pre, bets_control_after],
        [interval_i + LINE_SHIFT_Y, interval_i + LINE_SHIFT_Y],
        color=utils.Colors.CONTROL,
        label="Control" if interval_i == 0 else None
    )
    plt.scatter(
        [(bets_control_pre+ bets_control_after)/2],
        [interval_i + LINE_SHIFT_Y],
        marker=">" if bets_control_pre < bets_control_after else "<",
        s=45, color=utils.Colors.CONTROL,
    )

plt.yticks(
    range(len(INTERVALS)),
    [
        f"[{a:.0%}, {b:.0%}" + (")" if b != 1 else "]")
        for a, b in INTERVALS[::-1]
    ]
)
plt.ylabel("AI system confidence          ")
plt.xlabel("Average bet value (¢)")

plt.legend(
    loc="lower left",
    bbox_to_anchor=(-0.4, 1),
    ncols=3,
    fancybox=False,
    edgecolor="black",
    columnspacing=0.44,
    handlelength=1.5,
)
plt.tight_layout(rect=(-0.02, 0, 1, 1.05))
plt.savefig("computed/figures/bet_distribution_change.pdf")
plt.show()

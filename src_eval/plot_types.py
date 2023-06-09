#!/usr/bin/env python3
import jezecek.fig_utils
import matplotlib.pyplot as plt
import argparse
import numpy as np
import sys
sys.path.append("src")
import utils

QUEUE_PLAN_XTICKS = [
    (0, "\naccurate"),
    (10, "intervention"),
    (15, "\n" + " " * 10 + "accurate"),
]


args = argparse.ArgumentParser()
args.add_argument("--overlay", default=None)
args.add_argument("-d", "--data", default="data/collected.jsonl")
args = args.parse_args()

data_by_user_math_ci = utils.load_data(
    args.data, "types_math_intervention_ci", min_length=31
)
data_by_user_trivia_ci = utils.load_data(
    args.data, "types_trivia_intervention_ci", min_length=31
)

for data_local in data_by_user_math_ci:
    for line in data_local:
        line["affected"] = "question_tag_math" in line["question"]["question"]
for data_local in data_by_user_trivia_ci:
    for line in data_local:
        line["affected"] = "question_tag_trivia" in line["question"]["question"]

data_by_user = data_by_user_math_ci + data_by_user_trivia_ci

print(
    f"{len(data_by_user)} users with {np.average([len(x) for x in data_by_user]):.1f} questions on average"
)

QUEUE_LENGHT = 60
# a is control, b is affected
bet_vals_a = [[] for _ in range(QUEUE_LENGHT)]
bet_vals_b = [[] for _ in range(QUEUE_LENGHT)]
user_correct_a = [[] for _ in range(QUEUE_LENGHT)]
user_correct_b = [[] for _ in range(QUEUE_LENGHT)]

user_payoff = []
for data_local in data_by_user:
    # take first 10 as normalization to 0.06
    offset_bet = (
        0.06 - np.average([x["user_bet_val"] for x in data_local[:10]])
    )
    # take first 10 as normalization to 80%
    offset_correct = (
        0.8 - np.average([
            x["user_decision"] == x["question"]["ai_is_correct"]
            for x in data_local[:10]
        ])
    )
    user_payoff_local = []
    for i in range(min(QUEUE_LENGHT, len(data_local))):
        user_payoff_local.append(data_local[i]["user_bet_val"])
        if data_local[i]["affected"]:
            bet_vals = bet_vals_b
            user_correct = user_correct_b
        else:
            bet_vals = bet_vals_a
            user_correct = user_correct_a

        bet_vals[i].append(
            data_local[i]["user_bet_val"] + offset_bet
        )
        user_correct[i].append(
            (data_local[i]["user_decision"] == data_local[i]
             ["question"]["ai_is_correct"]) + offset_correct
        )

fig = plt.figure(figsize=(4.5, 1.8))
xticks_fine = np.linspace(15, QUEUE_LENGHT, 500)


def safe_average(arr):
    if arr:
        return np.average(arr)
    else:
        print(arr)
        return 0.06

poly_fits = []
for user_correct, bet_vals, first_bet_val, marker, line_type, label in [
    (user_correct_a, bet_vals_a, 1, "o", "#2d7f2f", "Unaffected"),
    (user_correct_b, bet_vals_b, 0.2, "^", "#7f2d2d", "Affected"),
]:
    # plot points
    plt.scatter(
        [-10] + [
            i for i in range(QUEUE_LENGHT)
            if (label == "Affected") or (i < 10 or i >= 15)
        ],
        [-10] + [
            np.average(bet_val) for i, bet_val in enumerate(bet_vals)
            if (label == "Affected") or (i < 10 or i >= 15)
        ],
        c=(
            [first_bet_val] +
            [
                np.average(user_correct) for i, user_correct in enumerate(user_correct)
                if (label == "Affected") or (i < 10 or i >= 15)
            ]
        ),
        cmap="RdYlGn",
        edgecolor="black",
        marker=marker,
        label=label,
        s=35,
        # alpha=0.8,
        zorder=-100,
        linewidth=0.5
    )


    # plot line
    poly_fit = np.poly1d(np.polyfit(
        range(15, QUEUE_LENGHT),
        [safe_average(bet_val) for bet_val in bet_vals[15:]], 3
    ))
    poly_fits.append(poly_fit)

    # contours hack
    # plt.plot(
    #     xticks_fine, 0.0003+poly_fit(xticks_fine), color="black", zorder=-100,
    #     linewidth=1.1,
    # )
    # plt.plot(
    #     xticks_fine, -0.0003+poly_fit(xticks_fine), color="black", zorder=-100,
    #     linewidth=1.1,
    # )
    # actual spline
    plt.plot(
        xticks_fine, poly_fit(xticks_fine), color=line_type,
        label=" ",
        linewidth=2.5,
        zorder=50,
    )

GAP_X = 32
plt.plot(
    [GAP_X, GAP_X],
    [poly_fits[0](GAP_X), poly_fits[1](GAP_X)],
    color="black",
    linewidth=2,
    zorder=100,
    linestyle="-"
)

plt.xlim(-2, None)
plt.ylim(0.04, 0.08)
plt.clim(0.2, 1)
plt.colorbar(label="User Correctness")
plt.xticks(
    [x_i for x_i, x in QUEUE_PLAN_XTICKS],
    [x for x_i, x in QUEUE_PLAN_XTICKS],
    linespacing=0.6
)

BET_VALS = np.round([i / 5 * 0.1 for i in range(5)], 2)
plt.yticks(BET_VALS[2:], [f"{x:.2f}" for x in BET_VALS[2:]])
plt.ylabel("Trust (bet value)")
plt.legend(
    ncol=2,
    fancybox=False, edgecolor="black",
    labelspacing=-1,
    columnspacing=0.5,
    handlelength=1.3,
)
plt.tight_layout(pad=0.1)
plt.savefig(f"computed/figures/trust_types.pdf")
plt.show()

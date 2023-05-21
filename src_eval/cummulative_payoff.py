#!/usr/bin/env python3

import jezecek.fig_utils
import matplotlib.pyplot as plt
import argparse
import numpy as np
import sys
sys.path.append("src")
import utils

QUEUE_PLAN_XTICKS = [
    (0, "\ncalibrated"),
    (10, "intervention"),
    (15, "\n" + " " * 10 + "calibrated"),
]
QUEUE_TO_NAME = {
    "control_long": "Control",
    "intervention_ci_long": "Confidently Incorrect",
    "intervention_uc_long": "Unconfidently Correct",
}
LEGEND_KWARGS = {
    "borderpad": 0.3,
    "labelspacing": 0.0,
    "handletextpad": 0.5,
    "handlelength": 1,
    "edgecolor": "black"
}

args = argparse.ArgumentParser()
args.add_argument("-d", "--data", default="data/collected.jsonl")
args = args.parse_args()

QUEUE_LENGHT = 60
fig = plt.figure(figsize=(4.5, 1.8))

linear_alphas = []
for queue, queue_color in [
    ("control_long", "#2da155"),
    ("intervention_uc_long", "#feb57f"),
    ("intervention_ci_long", "#a50026"),
]:
    data_by_user = utils.load_data(args.data, queue)
    user_payoff = [[] for _ in range(QUEUE_LENGHT)]
    for data_local in data_by_user:
        for i in range(len(data_local)):
            user_payoff[i].append(
                data_local[i]["user_balance"] * 100
            )

    # plot line after intervention
    poly_fit_coef = np.polyfit(
        range(15, QUEUE_LENGHT),
        [np.average(amount) for amount in user_payoff[15:]],
        deg=1
    )
    poly_fit = np.poly1d(poly_fit_coef)
    xticks_fine = np.linspace(15, QUEUE_LENGHT, 500)
    plt.plot(
        xticks_fine, poly_fit(xticks_fine), '-', color="black", zorder=-100
    )

    # plot points
    plt.plot(
        range(QUEUE_LENGHT),
        [np.average(amount) for amount in user_payoff],
        label=f"{QUEUE_TO_NAME[queue]}", color=queue_color
    )
    linear_alphas.append(poly_fit_coef[0])

# plt.ylim(0.03, 0.11)
plt.xticks(
    [x_i for x_i, x in QUEUE_PLAN_XTICKS],
    [x for x_i, x in QUEUE_PLAN_XTICKS],
    linespacing=0.6
)

# BET_VALS = np.round([i / 5 * 0.1 for i in range(5 + 1)], 2)
# plt.yticks(BET_VALS[2:], [f"{x:.2f}" for x in BET_VALS[2:]])
plt.ylabel("Accumulated ¢")

# legend1 = pyplot.legend(plot_lines[0], ["algo1", "algo2", "algo3"], loc=1)
# pyplot.legend([l[0] for l in plot_lines], parameters, loc=4)
lines = plt.gca().get_lines()
legend1 = plt.legend(
    [l for l in lines if not l.get_label().startswith("_")],
    [l.get_label() for l in lines if not l.get_label().startswith("_")],
    loc="upper left", **LEGEND_KWARGS
)
legend2 = plt.legend(
    [l for l in lines if not l.get_label().startswith("_")],
    [f"$\\alpha = {x:.1f}$" for x in linear_alphas],
    loc="lower right", title="Gain Speed", **LEGEND_KWARGS
)
plt.gca().add_artist(legend1)
# plt.legend(legend_handles, ["a", "b", "c"])
plt.tight_layout(pad=0.1)
plt.savefig(f"computed/figures/cummulative_payoff.pdf")
plt.show()

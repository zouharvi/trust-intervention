#!/usr/bin/env python3

import jezecek.fig_utils
import matplotlib.pyplot as plt
import argparse
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from matplotlib import patches
import sys
sys.path.append("src")
import utils

QUEUE_PLAN_XTICKS = [
        (4, "\n" + "accurate"),
        (14, "intervention"),
        (35, "\n" + "accurate"),
]
QUEUE_TO_NAME = {
    "control_long": "Control",
    "intervention_ci_long": "Conf. Incorr.",
    "intervention_uc_long": "Unconf. Corr.",
}
LEGEND_KWARGS = {
    "borderpad": 0.25,
    "labelspacing": -0.1,
    "handletextpad": 0.5,
    "handlelength": 1,
    "edgecolor": "black"
}

args = argparse.ArgumentParser()
args.add_argument("-d", "--data", default="data/collected.jsonl")
args = args.parse_args()

QUEUE_LENGHT = 60
fig = plt.figure(figsize=(4, 1.6))

plt.gca().add_patch(
    patches.Rectangle(
        (9.5, 0), 5.5, 400,
        zorder=-100,
        color="gray",
        alpha=0.5
    ),
)

linear_alphas = []
for queue, queue_color in [
    ("control_long", utils.Colors.CONTROL),
    ("intervention_uc_long", utils.Colors.UC),
    ("intervention_ci_long", utils.Colors.CI),
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
        xticks_fine, poly_fit(xticks_fine) - 5, '-', color="black", zorder=-100
    )
    Xs = list(range(QUEUE_LENGHT))
    Ys = [np.average(amount) for amount in user_payoff]

    # plot points
    plt.plot(
        Xs, Ys,
        label=f"{QUEUE_TO_NAME[queue]} $\\alpha$={poly_fit_coef[0]:.1f}", color=queue_color,
        alpha=0.7
    )

    # #add constant to predictor variables
    # Xs = sm.add_constant(Xs)
    # #fit linear regression model
    # model = sm.OLS(Ys, Xs).fit()
    # for x in range (0, 3):
    #     print(model.pvalues[x])

plt.ylim(0, 305)
plt.tick_params(axis="x", length=0)
plt.xticks(
    [x_i for x_i, x in QUEUE_PLAN_XTICKS],
    [x for x_i, x in QUEUE_PLAN_XTICKS],
    linespacing=0.6
)

# BET_VALS = np.round([i / 5 * 0.1 for i in range(5 + 1)], 2)
# plt.yticks(BET_VALS[2:], [f"{x:.2f}" for x in BET_VALS[2:]])
plt.ylabel("Accumulated ¢")

lines = plt.gca().get_lines()
legend1 = plt.legend(
    [l for l in lines if not l.get_label().startswith("_")],
    [l.get_label() for l in lines if not l.get_label().startswith("_")],
    loc="upper left", fancybox=False, **LEGEND_KWARGS
)
# legend2 = plt.legend(
#     [l for l in lines if not l.get_label().startswith("_")],
#     [f"$\\alpha = {x:.1f}$" for x in linear_alphas],
#     loc="lower right", title="Gain Speed", **LEGEND_KWARGS,
#     ncol=1, columnspacing=0
# )
plt.gca().add_artist(legend1)
plt.tight_layout(pad=0.1)
plt.savefig(f"computed/figures/cummulative_payoff.pdf")
plt.show()

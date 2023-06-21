#!/usr/bin/env python3

import argparse
import numpy as np
import jezecek.fig_utils
import matplotlib.pyplot as plt
import sys
sys.path.append("src")
import utils

args = argparse.ArgumentParser()
args.add_argument("-d", "--data", default="data/collected.jsonl")
args = args.parse_args()

QUEUE_LENGHT = 60

data_to_plot_acc = []
data_to_plot_bet = []
data_to_plot_alpha = []
data_to_plot_beta = []

# hack because I don't have Shehzaad's betas
BETAS = [None, -0.5, -0.8, -1.4, -1.2, -0.9,]

for queue in [
    "control_long",
    "intervention_ci_1_long",
    "intervention_ci_3_long",
    "intervention_ci_long",
    "intervention_ci_7_long",
    "intervention_ci_9_long",
]:
    data_by_user = utils.load_data(args.data, queue)

    bet_vals = [[] for _ in range(QUEUE_LENGHT)]
    user_correct = [[] for _ in range(QUEUE_LENGHT)]
    user_payoff = [[] for _ in range(QUEUE_LENGHT)]

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
        for i in range(min(QUEUE_LENGHT, len(data_local))):
            bet_vals[i].append(
                # data_local[i]["times"]["decision"] + data_local[i]["times"]["bet"]
                (data_local[i]["user_bet_val"] + offset_bet) * 100
            )
            user_correct[i].append(
                (data_local[i]["user_decision"] == data_local[i]
                 ["question"]["ai_is_correct"]) + offset_correct
            )
            user_payoff[i].append(data_local[i]["user_balance"] * 100)

    poly_fit_coef = np.polyfit(
        range(19, QUEUE_LENGHT),
        [np.average(amount) for amount in user_payoff[19:]],
        deg=1
    )
    poly_fit = np.poly1d(poly_fit_coef)

    payoff_after_intervention = (
        np.average(user_payoff[QUEUE_LENGHT - 1]) -
        np.average(user_payoff[19])
    )
    queue_name = (
        queue
        .replace("intervention_ci_long", "intervention_ci_5_long")
        .replace("control_long", "intervention_ci_0_long")
    )
    queue_name = "".join([x for x in queue_name if x.isdigit()])
    bet_before = np.average(bet_vals[19:40])
    acc_before = np.average(user_correct[19:40])
    bet_after = np.average(bet_vals[40:])
    acc_after = np.average(user_correct[40:])

    data_to_plot_acc.append((acc_before, acc_after))
    data_to_plot_bet.append((bet_before, bet_after))
    data_to_plot_alpha.append((poly_fit_coef[0], payoff_after_intervention))
    data_to_plot_beta.append(BETAS.pop(0))


fig = plt.figure(figsize=(4, 2.5))

ax = plt.subplot(2, 2, 1)
ax.scatter(
    range(6),
    [100 * x[0] for x in data_to_plot_acc],
    color=utils.Colors.NEUTRAL1,
    s=22,
)
ax.scatter(
    range(6),
    [100 * x[1] for x in data_to_plot_acc],
    color=utils.Colors.NEUTRAL2,
    s=22,
)
ax.set_ylabel("Accuracy (%)")
ax.set_xticks([], [])

ax = plt.subplot(2, 2, 2)
ax.scatter(
    range(6),
    [x[0] for x in data_to_plot_bet],
    color=utils.Colors.NEUTRAL1,
    s=22,
)
ax.scatter(
    range(6),
    [x[1] for x in data_to_plot_bet],
    color=utils.Colors.NEUTRAL2,
    s=22,
)
ax.set_ylabel("Bet value (¢)")
ax.yaxis.set_label_position("right")
ax.yaxis.tick_right()
ax.set_xticks([], [])


ax = plt.subplot(2, 2, 3)
ax.scatter(
    range(6),
    [x[0] for x in data_to_plot_alpha],
    color=utils.Colors.NEUTRAL1,
    s=22,
)
for i, x in enumerate(data_to_plot_alpha):
    ax.text(
        **({"x": i + 0.4, "y": x[0] - 0.15} if i < 3 else {"x": i - 0.3, "y": x[0] - 0.15} if i < 5 else {"x": i - 0.4, "y": x[0] + 0.2}),
        s=f"{x[1]:.0f}¢",
        ha="center", va="top",
        size="small"
    )
# ax.scatter(
#     range(6),
#     [x[1] for x in data_to_plot_alpha],
#     color=utils.Colors.NEUTRAL2,
# )
ax.set_ylabel("α (gain ¢)")
ax.set_xlabel("Intervention size")
ax.set_xticks([0, 1, 2, 3, 4, 5], [0, 1, 3, 5, 7, 9])


ax = plt.subplot(2, 2, 4)
ax.scatter(
    range(1, 6),
    [x for x in data_to_plot_beta[1:]],
    color=utils.Colors.NEUTRAL1,
    s=22,
)
ax.set_ylabel("$\\beta_2$", labelpad=-0.2)
ax.set_xlabel("Intervention size")
ax.yaxis.set_label_position("right")
ax.yaxis.tick_right()
ax.set_xticks([0, 1, 2, 3, 4, 5], [0, 1, 3, 5, 7, 9])


plt.tight_layout(pad=0.2, w_pad=0, h_pad=0.3)
plt.savefig("computed/figures/intervention_size.pdf")
plt.show()

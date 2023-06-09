#!/usr/bin/env python3

import jezecek.fig_utils
import matplotlib.pyplot as plt
import argparse
import numpy as np
import matplotlib.patches as patches
import sys
sys.path.append("src")
import utils

args = argparse.ArgumentParser()
args.add_argument("-d", "--data", default="data/collected.jsonl")
args = args.parse_args()

data_by_user = utils.load_data(args.data, queue=None)

print(
    f"{len(data_by_user)} users with {np.average([len(x) for x in data_by_user]):.1f} questions on average"
)

QUEUE_LENGHT = 60

times_decision = [[] for _ in range(QUEUE_LENGHT)]
times_bet = [[] for _ in range(QUEUE_LENGHT)]
times_next = [[] for _ in range(QUEUE_LENGHT)]

for data_local in data_by_user:
    user_payoff_local = []
    for i in range(min(QUEUE_LENGHT, len(data_local))):
        user_payoff_local.append(data_local[i]["user_bet_val"])
        times_decision[i].append(data_local[i]["times"]["decision"] / 1000)
        times_bet[i].append(data_local[i]["times"]["bet"] / 1000)
        times_next[i].append(data_local[i]["times"]["next"] / 1000)

fig = plt.figure(figsize=(4, 1.7))
xticks_fine = np.linspace(0, QUEUE_LENGHT, 500)

times_decision = [np.median(x) for x in times_decision]
times_bet = [np.median(x) for x in times_bet]
times_next = [np.median(x) for x in times_next]

print(
    f"Average stimulus: {np.average(times_decision)+np.average(times_bet)+np.average(times_next):.1f}s"
)
print(
    f"Average total: {(sum(times_decision)+sum(times_bet)+sum(times_next))/60:.1f}m"
)

# plot points
plt.stackplot(
    range(1, QUEUE_LENGHT + 1),
    times_decision,
    times_bet,
    times_next,
    labels=["Decision", "Bet", "Next"]
)

ax = plt.gca()
TEXT_Y = 22
for x in [10, 35]:
    rect = patches.FancyBboxPatch(
        (x - 3, TEXT_Y - 5), 7, 8,
        facecolor='white',
        edgecolor="black", linewidth=1,
        boxstyle=patches.BoxStyle("Round", rounding_size=0.5),
    )
    ax.add_patch(rect)
    plt.plot(
        [x, x],
        [TEXT_Y-5.5, times_decision[x] + times_bet[x] + times_next[x]+1],
        color="black"
    )

    plt.text(
        x, TEXT_Y - 4,
        s=f"{times_decision[x-1]:.1f}s",
        color="#5c8c5c",
        ha="center", fontdict={"size": 9.5}
    )
    plt.text(
        x, TEXT_Y - 2,
        s=f"{times_bet[x-1]:.1f}s",
        color="#b3584d",
        ha="center", fontdict={"size": 9.5}
    )
    plt.text(
        x, TEXT_Y,
        s=f"{times_next[x-1]:.1f}s",
        color="#2f4e85",
        ha="center", fontdict={"size": 9.5}
    )

plt.xlim(1, 60)

# reverse order
handles, labels = ax.get_legend_handles_labels()
plt.legend(
    handles[::-1], labels[::-1],
    **{
        "borderpad": 0.25,
        "labelspacing": -0.1,
        "handletextpad": 0.5,
        "handlelength": 1,
        "edgecolor": "black"
    })

plt.ylabel("Time (s)")
plt.tight_layout(pad=0.1)
plt.savefig(f"computed/figures/times_composite.pdf")
plt.show()

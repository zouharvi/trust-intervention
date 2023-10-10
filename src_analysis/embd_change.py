#!/usr/bin/env python3

import pickle
import numpy as np
import random
import jezecek.fig_utils
import matplotlib as mpl
import matplotlib.pyplot as plt
import collections
from matplotlib import patches
import utils

random.seed(0)
# mpl.rc('text', usetex = True)

data = pickle.load(open("computed/embd.pkl", "rb"))

data_processed = collections.defaultdict(lambda: collections.defaultdict(list))

for queue_name, queue_users in data.items():
    for embds in queue_users:
        embds = np.array(embds)
        for embd_i, embd in enumerate(embds[1:]):
            data_processed[queue_name][embd_i].append(embd * embds[embd_i])

plt.figure(figsize=(3.7, 1.7))

plt.gca().add_patch(
    patches.Rectangle(
        (9.5, 0), 5.5, 1,
        zorder=-100,
        color="gray",
        alpha=0.5
    ),
)

QUEUE_TO_NAME = {
    "control": "Control",
    "intervention_ci": "Confidently Incorrect",
    "intervention_uc": "Unconfidently Correct",
}
for queue in [
    "control",
    "intervention_ci",
    "intervention_uc",
]:
    plt.plot(
        [np.average(x) for x in data_processed[queue].values()],
        label=QUEUE_TO_NAME[queue],
        color=utils.COLORS[queue]
    )

plt.ylim(0, 0.35)
plt.ylabel("Inner product with\nprevious hidden state")
plt.xticks([])
plt.xlabel("Experiment progression")
plt.legend(
    fancybox=False, edgecolor="black",
    columnspacing=0.5,
    labelspacing=0.1,
    handlelength=1.3,
    loc="lower right"
)

plt.tight_layout(pad=0.2)
plt.savefig("computed/figures/hidden_vector_change.pdf")
plt.show()

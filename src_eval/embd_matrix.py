#!/usr/bin/env python3

import pickle
import numpy as np
import random
import jezecek.fig_utils
import matplotlib as mpl
import matplotlib.pyplot as plt
import collections

random.seed(0)
mpl.rc('text', usetex = True)

data = pickle.load(open("computed/embd.pkl", "rb"))

data_processed = collections.defaultdict(list)

for queue_name, queue_users in data.items():
    for embds in queue_users:
        data_processed[queue_name + "_pre"] += embds[:10]
        data_processed[queue_name + "_mid"] += embds[10:15]
        data_processed[queue_name + "_post"] += embds[20:]

print({k: len(v) for k, v in data_processed.items()})


def get_group_sim(group1, group2):
    # print(group1, group2)
    group1 = random.sample(data_processed[group1], k=140)
    group2 = random.sample(data_processed[group2], k=140)
    # group1 = data_processed[group1]
    # group2 = data_processed[group2]

    sims = [
        # cosine similarity
        np.array(v1)*np.array(v2)
        # np.linalg.norm(np.array(v1)-np.array(v2))
        # np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        for v1 in group1
        for v2 in group2
    ]
    return np.average(sims)

img = np.empty((6, 6,))
img[:] = 0

fig = plt.figure(figsize=(4.1, 2))
for group1_i, group1_name in enumerate(["control", "intervention_ci"]):
    for group2_i, group2_name in enumerate(["control", "intervention_ci"]):
        for pos1_i, pos1_name in enumerate(["pre", "mid", "post"]):
            for pos2_i, pos2_name in enumerate(["pre", "mid", "post"]):
                sim = get_group_sim(
                    group1_name + "_" + pos1_name,
                    group2_name + "_" + pos2_name
                )
                print(
                    group1_name + "_" + pos1_name,
                    group2_name + "_" + pos2_name, 
                    group1_i * 3 + pos1_i, f"({group1_i} * 3 + {pos1_i})", group2_i * 3 + pos2_i, f"({group2_i} * 3 + {pos2_i})"
                    "\t\t\t", f"{sim:.2f}"
                )
                img[group1_i * 3 + pos1_i, group2_i * 3 + pos2_i] = sim
                plt.text(
                    group2_i * 3 + pos2_i, group1_i * 3 + pos1_i, 
                    f"{sim:.2f}", va="center", ha="center",
                    color="black" if sim < 0.2 else "white"
                )

plt.imshow(img, aspect="auto", cmap="Greys")
plt.colorbar(pad=0.02)
plt.xticks(range(6), ["pre", "mid\n\\textbf{Control}", "post", "pre", "mid\n\\textbf{Intervention CI}", "post"])
plt.yticks(range(6), ["pre", "\\textbf{Control}   mid", "post", "pre", "\\textbf{Int. CI}   mid", "post"])
# no idea why things are off by 0.5
plt.plot([2.5, 2.5], [-0.5, 5.5], color="black")
plt.plot([-0.5, 5.5], [2.5, 2.5], color="black")
plt.ylim(-0.5, 5.5)
plt.xlim(-0.5, 5.5)
plt.tight_layout(pad=0.2)
plt.savefig("computed/figures/hidden_vector_similarity.pdf")
plt.show()

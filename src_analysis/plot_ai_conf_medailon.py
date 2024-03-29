#!/usr/bin/env python3

import jezecek.fig_utils
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import argparse

AI_CONF_TYPES = {
    "base": {
        "correct": (0.7, (0.45, 0.8)),
        "incorrect": (0.3, (0.2, 0.55)),
        "name": "\naccurate",
    },
    "vague": {
        "correct": (0.7, (0.45, 0.55)),
        "incorrect": (0.3, (0.4, 0.5)),
        "name": "vague",
    },
    "ci": {
        "correct": (0, (0.7, 1.0)),
        "incorrect": (1, (0.7, 1.0)),
        "name": "confidently\nincorrect",
    },
    "uc": {
        "correct": (1, (0.1, 0.4)),
        "incorrect": (0, (0.1, 0.4)),
        "name": "unconfidently\ncorrect",
    }
}

args = argparse.ArgumentParser()
args.add_argument("-ait", "--ai-type", default="base")
args = args.parse_args()

ai_conf_type = AI_CONF_TYPES[args.ai_type]

fig = plt.figure(figsize=(2, 1.4))
ax = plt.gca()

rect = patches.Rectangle(
    (0, ai_conf_type["correct"][1][0]),
    width=ai_conf_type["correct"][0], height=ai_conf_type["correct"][1][1] -
    ai_conf_type["correct"][1][0],
    linewidth=2, edgecolor='#264c1d', facecolor='#679b5a', clip_on=False,
)
ax.add_patch(rect)
rect = patches.Rectangle(
    (-ai_conf_type["incorrect"][0] - 0.03, ai_conf_type["incorrect"][1][0]),
    width=ai_conf_type["incorrect"][0], height=ai_conf_type["incorrect"][1][1] -
    ai_conf_type["incorrect"][1][0],
    linewidth=2, edgecolor='#722020', facecolor='#d33d3d', clip_on=False,
)
ax.add_patch(rect)
# ax.spines['left'].set_position(('data', 0.0))
ax.spines['right'].set_color('none')
# ax.spines['top'].set_color('none')
ax.spines['left'].set_color('none')
# ax.spines['bottom'].set_color('none')

plt.ylim(0, 1)
plt.xlim(-1, 1)
plt.xticks(
    [-0.5, 0.5],
    [
        f"Incorrect\n{ai_conf_type['incorrect'][0]:.0%}",
        f"Correct\n{ai_conf_type['correct'][0]:.0%}"
    ],
    minor=False
)
ax.tick_params(axis="x", bottom=False)
ax.tick_params(axis="y", left=False)
plt.yticks([0, 0.5, 1], ["0%", "50%", "100%"])
plt.title(
    AI_CONF_TYPES[args.ai_type]["name"],
    fontdict={"fontsize": 11}
)

# draw border around
rect = patches.FancyBboxPatch(
    # (lower-left corner), width, height
    (0.02, 0.02), 0.96, 0.96, fill=False, color="k", linewidth=2,
    zorder=1000, transform=fig.transFigure, figure=fig,
    boxstyle=patches.BoxStyle("Round", rounding_size=0.1, pad=0)
)
fig.patches.extend([rect])
plt.tight_layout(rect=[-0.05, -0.07, 1.0, 1.05])
plt.savefig(f"computed/figures/medailon_{args.ai_type}.pdf")
plt.show()

# for AI_TYPE in "base" "vague" "ci" "uc"; do DISPLAY="" ./src_analysis/plot_ai_conf_medailon.py -ait ${AI_TYPE}; done

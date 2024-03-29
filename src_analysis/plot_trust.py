#!/usr/bin/env python3

# import jezecek.fig_utils
import matplotlib.pyplot as plt
import argparse
import numpy as np
from skimage.transform import resize as resize_img
from sklearn.metrics import r2_score
import pickle
from matplotlib import patches
import utils

QUEUE_PLAN_XTICKS = {
    "intervention_ci_long": [
        (4, "\n" + "accurate"),
        (14, "conf. incorr."),
        (35, "\n" + "accurate"),
    ],
    "intervention_uc_long": [
        (4, "\n" + "accurate"),
        (14, "unconf. corr."),
        (35, "\n" + "accurate"),
    ],
    "control_long": [
        (0, "\n" + "accurate"),
    ],
}

args = argparse.ArgumentParser()
args.add_argument("-q", "--queue", default="control_long")
args.add_argument("--overlay", default=None)
args.add_argument("--overlay-up", action="store_true")
args.add_argument("--rect", action="store_true")
args.add_argument("--no-norm", action="store_true")
args.add_argument("-d", "--data", default="data/collected_users.jsonl")
args = args.parse_args()

data_by_user = utils.load_data(args.data, args.queue)

print(
    f"{len(data_by_user)} users with {np.average([len(x) for x in data_by_user]):.1f} questions on average"
)

QUEUE_LENGHT = max(len(data_local) for data_local in data_by_user)
QUEUE_LENGHT = 60
bet_vals = [[] for _ in range(QUEUE_LENGHT)]
user_correct = [[] for _ in range(QUEUE_LENGHT)]

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
        bet_vals[i].append(
            # data_local[i]["times"]["decision"] + data_local[i]["times"]["bet"]
            (data_local[i]["user_bet_val"] + (0 if args.no_norm else offset_bet))*100
        )
        user_correct[i].append(
            (data_local[i]["user_decision"] == data_local[i]
             ["question"]["ai_is_correct"]) + (0 if args.no_norm else offset_correct)
        )
    # guaranteed to be the last
    user_payoff.append(data_local[i]["user_balance"])
print(f"Average payoff {np.average(user_payoff):.2f}")
print(f"Total payoff {sum(user_payoff):.2f}")

fig = plt.figure(figsize=(4.4, 1.7))
xticks_fine = np.linspace(0, QUEUE_LENGHT, 500)

if args.rect:
    plt.gca().add_patch(
        patches.Rectangle(
            (9.5, 0), 5.5, 9,
            zorder=-100,
            color="gray",
            alpha=0.5
        ),
    )

# plot histogram
im_correctness = np.array([
    [np.average(user_correct) for user_correct in user_correct]
])
im_correctness = resize_img(im_correctness, (8, 290))
fig.figimage(
    X=im_correctness, xo=55,
    yo=fig.bbox.ymax - 24 if not args.overlay_up else fig.bbox.ymax - 16,
    cmap="RdYlGn", vmin=0.2, vmax=1
)

# plot points
scatter_x = list(range(QUEUE_LENGHT))
scatter_y = [np.average(bet_val) for bet_val in bet_vals]
plt.scatter(
    scatter_x, scatter_y,
    c=[np.average(user_correct) for user_correct in user_correct],
    cmap="RdYlGn",
    edgecolor="black"
)

# compute r2 with leave-one-out strategy
scatter_y_pred = []
for i in range(len(scatter_x)):
    scatter_x_local = scatter_x[:i]+scatter_x[i+1:]
    scatter_y_local = scatter_y[:i]+scatter_y[i+1:]
    poly_fit = np.poly1d(np.polyfit(
        scatter_x_local, scatter_y_local, 3
    ))
    scatter_y_pred.append(poly_fit([scatter_x[i]])[0])

poly_fit_r2 = r2_score(scatter_y, scatter_y_pred)
print(f"{args.queue:>20} | R^2: {poly_fit_r2:.3f}")

# plot line
poly_fit = np.poly1d(np.polyfit(
    scatter_x, scatter_y, 3
))


plt.plot(
    xticks_fine, poly_fit(xticks_fine), '-', color="black", zorder=-100
)
pickle.dump((im_correctness, poly_fit), open(
    f"computed/overlay/{args.queue}.pkl", "wb"))

if args.overlay:
    im_correctness_other, poly_fit_other = pickle.load(
        open(f"computed/overlay/{args.overlay}.pkl", "rb"))
    plt.plot(
        xticks_fine, poly_fit_other(xticks_fine), '-',
        color="black", zorder=-100, alpha=0.3
    )

    # GAP_X = 45
    # plt.plot(
    #     [GAP_X, GAP_X],
    #     [poly_fit(GAP_X), poly_fit_other(GAP_X)],
    #     color="gray",
    #     linewidth=2,
    #     zorder=-10,
    #     linestyle="--"
    # )
    fig.figimage(
        X=im_correctness_other, xo=55,
        yo=fig.bbox.ymax - 24 if args.overlay_up else fig.bbox.ymax - 16,
        cmap="RdYlGn", vmin=0.2, vmax=1, alpha=0.5
    )

if args.no_norm:
    plt.ylim(4, 12)
else:
    plt.ylim(4, 9)
plt.clim(0.2, 1)
plt.colorbar(label="User Correctness")
if args.queue in QUEUE_PLAN_XTICKS:

    plt.tick_params(axis="x", length=0)
    plt.xticks(
        [x_i for x_i, x in QUEUE_PLAN_XTICKS[args.queue]],
        [x for x_i, x in QUEUE_PLAN_XTICKS[args.queue]],
        linespacing=0.6, 
        ha="center"
    )
else:
    plt.xticks([0, 59], [".", "."], color="white")

BET_VALS = np.round([i / 5 * 0.1*100 for i in range(5)], 2)
plt.yticks(BET_VALS[2:], [f"{x:.0f}¢" for x in BET_VALS[2:]])
plt.ylabel("Trust (bet value)")
plt.tight_layout(pad=0.1)
plt.savefig(f"computed/figures/trust_{args.queue}.pdf")
plt.show()

# ./src_analysis/plot_trust.py -q control_long --overlay intervention_ci_long --overlay-up
# ./src_analysis/plot_trust.py -q intervention_ci_long --overlay control_long --rect
# ./src_analysis/plot_trust.py -q intervention_uc_long --overlay control_long --rect

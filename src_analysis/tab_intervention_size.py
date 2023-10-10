#!/usr/bin/env python3

import argparse
import numpy as np
import utils

args = argparse.ArgumentParser()
args.add_argument("-d", "--data", default="data/collected_users.jsonl")
args = args.parse_args()

QUEUE_LENGHT = 60
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
        for i in range(min(QUEUE_LENGHT, len(data_local))):
            bet_vals[i].append(
                # data_local[i]["times"]["decision"] + data_local[i]["times"]["bet"]
                (data_local[i]["user_bet_val"])*100
            )
            user_correct[i].append(
                (data_local[i]["user_decision"] == data_local[i]
                 ["question"]["ai_is_correct"])
            )
            user_payoff[i].append(data_local[i]["user_balance"]*100)

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
    print(
        f"{queue_name}",
        f"{payoff_after_intervention:.0f}",
        f"{poly_fit_coef[0]:.1f}",
        f"{bet_before:.1f}",
        f"{acc_before:.0%}".replace("%", "\\%"),
        f"{bet_after:.1f}",
        f"{acc_after:.0%}".replace("%", "\\%"),
        sep=" & ", end=" \\\\\n",
    )
#!/usr/bin/env python3

import utils
import numpy as np
from typing import List, Tuple

data = utils.load_data()
# take data from a single user
questions = [data[0][f"{x}"] for x in range(1, 30 + 1)]
print(f"{np.average([user['Reward'] for user in data]):.2f} average payout")
print(f"Always-hint decider gets payout of {30*0.1:.2f}")


def get_threshold_from_history(history: List[Tuple[float, bool]]):
    if len(history) == 0:
        return True, 0.5

    # sort by confidence
    history.sort(key=lambda x: x[0])
    # compute payout for all thresholds (just over and just under)
    thresholds = (
        [history[0][0] - 0.01] +
        [(x[0] + y[0]) / 2 for x, y in zip(history, history[1:])] +
        [history[-1][0] + 0.01]
    )
    best_threshold = None
    best_payout = -1
    for threshold in thresholds:
        payout = 0.15 * np.average([
            (conf >= threshold and correct) or (
                conf < threshold and not correct)
            for conf, correct in history
        ]) - 0.15 * np.average([
            (conf >= threshold and not correct) or (
                conf < threshold and correct)
            for conf, correct in history
        ])
        if payout > best_payout:
            best_payout = payout
            best_threshold = threshold

    return False, best_threshold


history = []
payout = 0
for question in questions:
    # consider all history
    do_hint, accept_threshold = get_threshold_from_history(history)
    conf = float("0." + question["question"]["conf"].removesuffix("%"))
    ai_correct = question["question"]["acc"] == "1"
    history.append((conf, ai_correct))

    # if we show the hint, we know the answer but have to pay 0.05
    if do_hint:
        payout += 0.10
        continue
    elif (
        conf >= accept_threshold and ai_correct or
        conf < accept_threshold and not ai_correct
    ):
        payout += 0.15
    else:
        payout -= 0.15

print(payout)

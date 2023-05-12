#!/usr/bin/env python3

import jezecek.fig_utils
import json
import matplotlib.pyplot as plt

# data = [json.loads(x) for x in open("data/intervention_ci.jsonl", "r")]
data = [json.loads(x) for x in open("data/control_0.jsonl", "r")]
print(data[0].keys())
plt.scatter(
    [x_i for x_i, x in enumerate(data) if x["user_decision"] == x["question"]["ai_is_correct"]],
    [x["user_bet_val"] for x_i, x in enumerate(data) if x["user_decision"] == x["question"]["ai_is_correct"]],
    label="Correct decision"
)
plt.scatter(
    [x_i for x_i, x in enumerate(data) if x["user_decision"] != x["question"]["ai_is_correct"]],
    [x["user_bet_val"] for x_i, x in enumerate(data) if x["user_decision"] != x["question"]["ai_is_correct"]],
    label="Incorrect decision"
)
plt.ylabel("Trust (bet value)")
plt.xlabel("Experiment Progress")
plt.legend()
plt.tight_layout()
plt.show()
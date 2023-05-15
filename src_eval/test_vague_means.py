#!/usr/bin/env python3

import json
import argparse
import numpy as np
import scipy.stats

args = argparse.ArgumentParser()
args.add_argument("-q", "--queue", default="control")
args.add_argument("-v", "--variable", default="user_bet_val")
args = args.parse_args()

data = [json.loads(x) for x in open("data/collected.jsonl", "r")]

def get_val(x):
    if args.variable == "user_bet_val":
        return x["user_bet_val"]
    elif args.variable == "user_correct":
        return x["user_decision"] == x["question"]["ai_is_correct"]

def get_distribution_by_queue(queue_name):
    # filter desired queue
    data_filter = [line for line in data if line["url_data"]["prolific_queue_name"] == queue_name]
    prolific_ids = {x["url_data"]["prolific_id"] for x in data_filter}
    data_by_user = [[x for x in data_filter if x["url_data"]["prolific_id"]==prolific_id] for prolific_id in prolific_ids]


    pre_intervention = [[get_val(x) for x_i, x in enumerate(data_local) if x_i >= 5 and x_i < 10] for data_local in data_by_user]
    post_intervention = [[get_val(x) for x_i, x in enumerate(data_local) if x_i >= 15 and x_i < 20] for data_local in data_by_user]
    # flatten
    pre_intervention = [x for l in pre_intervention for x in l]
    post_intervention = [x for l in post_intervention for x in l]

    return pre_intervention, post_intervention

pre_control, post_control = get_distribution_by_queue("control")
pre_intervention, post_intervention = get_distribution_by_queue("intervention_ci")

print(scipy.stats.ttest_ind(post_control, post_intervention, alternative="greater"))
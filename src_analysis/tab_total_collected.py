#!/usr/bin/env python3

import argparse
import numpy as np
import collections
import utils

QUEUE_TO_NAME = {
    "control_long": "Control",
    "intervention_ci_long": "Confidently Incorrect",
    "intervention_uc_long": "Unconfidently Correct",
}

args = argparse.ArgumentParser()
args.add_argument("-d", "--data", default="data/collected_users.jsonl")
args = args.parse_args()


data = utils.load_data(args.data)
data_count = collections.Counter([
    x["url_data"]["prolific_queue_name"]
    for data_local in data
    for x in data_local
])
data_user_count = collections.Counter([
    data_local[0]["url_data"]["prolific_queue_name"]
    for data_local in data
])

data_count["total"] = sum(data_count.values())
data_user_count["total"] = sum(data_user_count.values())

for queue in [
    "control_long",
    'intervention_ci_1_long', 'intervention_ci_3_long', 'intervention_ci_long', 'intervention_ci_7_long', 'intervention_ci_9_long',
    'types_trivia_intervention_ci', 'types_math_intervention_ci',
    'intervention_uc_long', "total",
]:
    print(
        (
            queue
            .replace('intervention_ci_long', "intervention_ci_5_long")
            .removesuffix("_long").removeprefix("types_")
            .capitalize().replace("_", " ")
            .replace("ci", "CI").replace("uc", "UC")
        ),
        data_user_count[queue],
        data_count[queue],
        sep=" & ", end=" \\\\\n"
    )

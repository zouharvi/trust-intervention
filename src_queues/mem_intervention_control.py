#!/usr/bin/env python3
import json
import pandas as pd
import statsmodels.formula.api as smf

def load_data(path="data/all_data.jsonl", queue=["control_no_vague", "intervention_ci_no_vague", "intervention_uc_no_vague"]):
    MULTI_USER_FIRST_QUEUE = {
        "604f684950227bd07a37376d": "control_no_vague",
        "63ea52b8342eff8b95ef0f95": "control_no_vague",
        "5dcf2c967beb290802f26b45": "control_no_vague",
    }
    print("loading data from path", path)
    data = [json.loads(x) for x in open(path, "r")]
    # filter desired queue
    data = [
        line for line in data
        if queue is None or line["url_data"]["prolific_queue_name"] in queue or True
    ]

    prolific_ids = list({x["url_data"]["prolific_id"] for x in data})
    # this weird why this isn't stable
    prolific_ids.sort()

    data_by_user = [
        [x for x in data if x["url_data"]["prolific_id"] == prolific_id]
        for prolific_id in prolific_ids
        if prolific_id not in MULTI_USER_FIRST_QUEUE or MULTI_USER_FIRST_QUEUE[prolific_id] in queue
    ]
    filtered_data_by_user = []
    for datum in data_by_user:

        # import pdb; pdb.set_trace()
        # if datum[-1]["user_bet_val"] < 0.5:# and datum[-1]["url_data"]["prolific_queue_name"] == "intervention_ci_no_vague":
        #     continue
        filtered_data_by_user.append(datum)

    print(
        f"Choosing {len(filtered_data_by_user)} users out of {len(data_by_user)}")

    return filtered_data_by_user

data = load_data()

records_uc = []
records_ci = []
records_control = []

for datum in data:
    if len(datum) != 30:
        continue
    for q in datum:
        record = {}

        if q["url_data"]["prolific_queue_name"] == "intervention_ci_no_vague":
            record["question"] = q['question_i'] +1 
            record["user_bet_val"] = q["user_bet_val"] * 100
            record["id"] = q["url_data"]["prolific_id"]
            record["intervention"] = 0 if record["question"] < 10 else 1
            records_ci.append(record)
            
            
for datum in data:
    if len(datum) != 30:
        continue
    for q in datum:
        record = {}

        if q["url_data"]["prolific_queue_name"] == "intervention_uc_no_vague":
            record["question"] = q['question_i'] +1 
            record["user_bet_val"] = q["user_bet_val"] * 100
            record["id"] = q["url_data"]["prolific_id"]
            record["intervention"] = 0 if record["question"] < 10 else 1
            records_uc.append(record)
            
            
for datum in data:
    if len(datum) != 30:
        continue
    for q in datum:
        record = {}

        if q["url_data"]["prolific_queue_name"] == "intervention_ci_no_vague":
            record["question"] = q['question_i'] +1 
            record["user_bet_val"] = q["user_bet_val"] * 100
            record["id"] = q["url_data"]["prolific_id"]
            record["intervention"] = 0 if record["question"] < 10 else 1
            records_control.append(record)


all_records_uc = pd.DataFrame(records_uc)
all_records_ci = pd.DataFrame(records_ci)
all_records_control = pd.DataFrame(records_control)


md = smf.mixedlm("user_bet_val ~ question + intervention  ", all_records_ci, groups=all_records_ci["id"])
mdf = md.fit()
print(mdf.summary())

md = smf.mixedlm("user_bet_val ~ question + intervention  ", all_records_uc, groups=all_records_uc["id"])
mdf = md.fit()
print(mdf.summary())

md = smf.mixedlm("user_bet_val ~ question + intervention  ", all_records_control, groups=all_records_control["id"])
mdf = md.fit()
print(mdf.summary())
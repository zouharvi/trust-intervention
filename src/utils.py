#!/usr/bin/env python3
from collections import defaultdict
import json
import sklearn.model_selection



def load_data(path="data/collected.jsonl", queue=None):
    import json
    MULTI_USER_FIRST_QUEUE = {
        "604f684950227bd07a37376d": "control_no_vague",
        "63ea52b8342eff8b95ef0f95": "control_no_vague",
        "5dcf2c967beb290802f26b45": "control_no_vague",
    }
    data = [json.loads(x) for x in open(path, "r")]
    # filter desired queue
    data = [
        line for line in data
        if queue is None or line["url_data"]["prolific_queue_name"] == queue
    ]

    prolific_ids = {x["url_data"]["prolific_id"] for x in data}
    data_by_user = [
        [x for x in data if x["url_data"]["prolific_id"] == prolific_id]
        for prolific_id in prolific_ids
        if prolific_id not in MULTI_USER_FIRST_QUEUE or MULTI_USER_FIRST_QUEUE[prolific_id] == queue
    ]
    return data_by_user

def load_split_data(simple=False):
    prolific_data = load_data()
    prolific_data = [
        (
            featurize_user_lines_simple(user)
            if simple else
            featurize_datum(user)
        )
        for user in prolific_data
    ]

    data_train, data_test = sklearn.model_selection.train_test_split(
        prolific_data,
        test_size=0.2,
        random_state=0
    )
    # print("train", len(data_train))
    # print("test", len(data_test))

    return data_train, data_test


def _avg_empty(arr):
    import numpy as np
    if not arr:
        return 0
    else:
        return np.average(arr)


def flatten(data):
    return [l for u in data for l in u]


def get_x(line):
    return [x for x, y in line]


def get_y(line, feature=0):
    return [y[feature] for x, y in line]

FEATURE_NAMES = [
    "model_confidence",
    "avg_prev_passage_show",
    "avg_prev_TP",
    "avg_prev_TN",
    "avg_prev_FN",
    "int_before", "int_inside", "int_after",
    # "question_num",
    # "time",
]


def featurize_datum(user_data):
    out = []

    prior_confusion_matrix = []
    
    for datum in user_data:


        out.append((
             _avg_empty([x and y for x, y in prior_confusion_matrix]),
                # average previoux FP
                _avg_empty([not x and y for x, y in prior_confusion_matrix]),
                # average previoux TN
                _avg_empty([
                    not x and not y
                    for x, y in prior_confusion_matrix
                ]),
                # average previoux FN
                _avg_empty([x and not y for x, y in prior_confusion_matrix]),
                float(datum['question']['ai_confidence'][:-1]),
                datum['question_i'] in range(0, 5) , 
                datum['question_i'] in range(5, 10) , 
                datum['question_i'] in range(10, 15) , 
                datum['question_i'] in range(15, 30) , 

                
                datum['url_data']['prolific_queue_name'] == 'control_no_vague',    
                datum['url_data']['prolific_queue_name'] == 'intervention_ci_no_vague',    

                datum['url_data']['prolific_queue_name'] == 'intervention_uc_no_vague',    


        )


        ,
        (
            datum["user_decision"] == "agree",
            datum['question']["ai_is_correct"],
            datum["user_bet_val"]
        ))
        prior_confusion_matrix.append((
            # Tx / Fx
            datum['question']["ai_is_correct"],
            # xP / xN
            datum["user_decision"] == "agree",
        ))

    return out
    










def featurize_user_lines(user):
    out = []
    prior_passage_saw = []
    prior_confusion_matrix = []
    for line in user.values():
        if type(line) != dict:
            continue
        out.append((
            # SOURCE
            (
                # model confidence
                float(line["question"]["conf"].removesuffix("%")) / 100,
                # average of previous passages
                _avg_empty(prior_passage_saw),
                # average previoux TP
                _avg_empty([x and y for x, y in prior_confusion_matrix]),
                # average previoux FP
                _avg_empty([not x and y for x, y in prior_confusion_matrix]),
                # average previoux TN
                _avg_empty([
                    not x and not y
                    for x, y in prior_confusion_matrix
                ]),
                # average previoux FN
                _avg_empty([x and not y for x, y in prior_confusion_matrix]),
                # intervention location
                line["q_no"] < 14, line["q_no"] >= 14 and line["q_no"] <= 18, line["q_no"] > 18,
                # question number
                # line["q_no"],
                line["q_no"] < 5
                # time
                # line["time"],
            ),

            # TARGET
            (
                # trust (user will click show hint)
                line["saw_passage1"],
                # trust (user will agree)
                line["response"] == "agree",
                # user success
                line["correct"],
                # AI is correct
                line["question"]["acc"] == "1"
            )
        ))
        prior_passage_saw.append(line["saw_passage1"])
        prior_confusion_matrix.append((
            # Tx / Fx
            line["correct"],
            # xP / xN
            line["response"] == "agree",
        ))

    return out


def featurize_user_lines_simple(user):
    out = []
    for line in user.values():
        if type(line) != dict:
            continue
        out.append((
            # SOURCE
            (
                # model confidence
                float(line["question"]["conf"].removesuffix("%")) / 100,
                # time
                # line["time"],
                # intervention location
                # line["q_no"] < 14, line["q_no"] >= 14 and line["q_no"] <= 18, line["q_no"] > 18,
                # question number
                # line["q_no"],
                # line["q_no"] < 5
            ),

            # TARGET
            (
                # trust (user will click show hint)
                line["saw_passage1"],
                # trust (user will agree)
                line["response"] == "agree",
                # user success
                line["correct"],
                # AI is correct
                line["question"]["acc"] == "1"
            )
        ))
    return out

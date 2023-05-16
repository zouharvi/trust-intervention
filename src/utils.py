#!/usr/bin/env python3
from collections import defaultdict

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


def load_split_data(simple=False, **kwargs):
    import sklearn.model_selection

    prolific_data = load_data(**kwargs)
    prolific_data = [
        (
            featurize_datum_line_simple(user)
            if simple else
            featurize_datum_line(user)
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


def featurize_datum_line(user_data):
    out = []
    prior_confusion_matrix = []
    prior_bet_val = []

    for datum in user_data:
        out.append((
            # x
            (
                # average previous bet value
                _avg_empty(prior_bet_val),
                # average previous TP
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
                # confidence
                float(datum['question']['ai_confidence'][:-1]) / 100,
                # question position
                datum['question_i'] in range(0, 10),
                datum['question_i'] in range(10, 15),
                datum['question_i'] in range(15, 30),
                # group indicator
                datum['url_data']['prolific_queue_name'] == 'control_no_vague',
                datum['url_data']['prolific_queue_name'] == 'intervention_ci_no_vague',
                datum['url_data']['prolific_queue_name'] == 'intervention_uc_no_vague',
            ),
            # y
            (
                datum["user_decision"],
                datum["user_bet_val"],
                datum["user_decision"] == datum['question']["ai_is_correct"],
                datum['question']["ai_is_correct"],
            )))
        prior_confusion_matrix.append((
            # Tx / Fx
            datum['question']["ai_is_correct"],
            # xP / xN
            datum["user_decision"],
        ))
        prior_bet_val.append(datum["user_bet_val"])
    return out


def featurize_datum_line_simple(user_data):
    out = []

    for datum in user_data:
        out.append((
            # x
            (
                float(datum['question']['ai_confidence'][:-1]) / 100,
                # question position
                datum['question_i'] in range(0, 10),
                datum['question_i'] in range(10, 15),
                datum['question_i'] in range(15, 30),
                # group indicator
                datum['url_data']['prolific_queue_name'] == 'control_no_vague',
                datum['url_data']['prolific_queue_name'] == 'intervention_ci_no_vague',
                datum['url_data']['prolific_queue_name'] == 'intervention_uc_no_vague',
            ),
            # y
            (
                datum["user_decision"],
                datum["user_bet_val"],
                datum["user_decision"] == datum['question']["ai_is_correct"],
                datum['question']["ai_is_correct"],
            )))
    return out
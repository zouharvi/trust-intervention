#!/usr/bin/env python3

from collections import defaultdict

# enum for colors
class Colors:
    CONTROL = "#4235b7"
    CI = "#b52f91"
    UC = "#3fafba"
COLORS={
    "control": Colors.CONTROL,
    "intervention_ci": Colors.CI,
    "intervention_uc": Colors.UC,
}

def load_data(path="data/all_data.jsonl", queue=None, verbose=False, min_length=60, **kwargs):
    import json
    MULTI_USER_FIRST_QUEUE = {
        "604f684950227bd07a37376d": "control_no_vague",
        "63ea52b8342eff8b95ef0f95": "control_no_vague",
        "5dcf2c967beb290802f26b45": "control_no_vague",
    }
    if type(queue) is str:
        queue = {queue}
    data = [json.loads(x) for x in open(path, "r")]
    # filter desired queue
    data = [
        line for line in data
        if (
            ("prolific_queue_name" in line["url_data"] and "prolific_id" in line["url_data"]) and
            (queue is None or line["url_data"]["prolific_queue_name"] in queue)
        )
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
    for user_lines in data_by_user:
        if len(user_lines) >= min_length:
            filtered_data_by_user.append(user_lines)

    if verbose:
        print(
            f"Choosing {len(filtered_data_by_user)} users out of {len(data_by_user)}"
        )

    return filtered_data_by_user


def load_data_as_df(path="data/all_data.jsonl", queue=None):
    raise Exception("Not Implemented")
    import json
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
        if queue is None or line["url_data"]["prolific_queue_name"] in queue
    ]

    prolific_ids = list({x["url_data"]["prolific_id"] for x in data})
    # this weird why this isn't stable
    prolific_ids.sort()

    user_data = defaultdict(list)
    study_data = defaultdict(list)
    for datum in control_data:
        user_data[datum['url_data']['prolific_id']].append(datum)
        study_data[datum['url_data']['study_id']].append(datum)

    data_by_user = [
        [x for x in data if x["url_data"]["prolific_id"] == prolific_id]
        for prolific_id in prolific_ids
        if prolific_id not in MULTI_USER_FIRST_QUEUE or MULTI_USER_FIRST_QUEUE[prolific_id] in queue
    ]

    filtered_data_by_user = []

    print(
        f"Choosing {len(filtered_data_by_user)} users out of {len(data_by_user)}")

    return filtered_data_by_user


def load_split_data(simple=False, **kwargs):
    import sklearn.model_selection

    prolific_data = load_data(**kwargs)
    prolific_data = [
        (
            featurize_datum_line_simple(user, **kwargs)
            if simple else
            featurize_datum_line(user, **kwargs)
        )
        for user in prolific_data
    ]

    data_train, data_test = sklearn.model_selection.train_test_split(
        prolific_data,
        test_size=0.2,
        random_state=0
    )

    return data_train, data_test


def load_split_data_all(simple=False, **kwargs):
    prolific_data = load_data(**kwargs)
    prolific_data = [
        (
            featurize_datum_line_simple(user, **kwargs)
            if simple else
            featurize_datum_line(user, **kwargs)
        )
        for user in prolific_data
    ]

    return prolific_data

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


def featurize_datum_line(user_data, question_classes=True, **kwargs):
    out = []
    prior_confusion_matrix = []
    prior_bet_val = []

    for user_line in user_data:
        val_x = [
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
            float(user_line['question']['ai_confidence'][:-1]) / 100,
            # group indicator
            # user_line['url_data']['prolific_queue_name'] == 'control_long',
            # user_line['url_data']['prolific_queue_name'] == 'intervention_ci_long',
            # user_line['url_data']['prolific_queue_name'] == 'intervention_uc_long',
        ] + ([
            # question position
            user_line['question_i'] in range(0, 10),
            user_line['question_i'] in range(10, 15),
            user_line['question_i'] in range(15, 30),
        ] if question_classes else [
            user_line['question_i']
        ])
        out.append((
            # x
            tuple(val_x),
            # y
            (
                user_line["user_decision"],
                user_line["user_bet_val"] * 100,
                user_line["user_decision"] == user_line['question']["ai_is_correct"],
                user_line['question']["ai_is_correct"],
            ))
        )
        prior_confusion_matrix.append((
            # Tx / Fx
            user_line['question']["ai_is_correct"],
            # xP / xN
            user_line["user_decision"],
        ))
        prior_bet_val.append(user_line["user_bet_val"])
    return out


def featurize_datum_line_simple(user_data, **kwargs):
    out = []

    for user_line in user_data:
        val_x = [
            float(user_line['question']['ai_confidence'][:-1]) / 100,
            # group indicator
            # user_line['url_data']['prolific_queue_name'] == 'control_long',
            # user_line['url_data']['prolific_queue_name'] == 'intervention_ci_long',
            # user_line['url_data']['prolific_queue_name'] == 'intervention_uc_long',
        ]
        out.append((
            # x
            tuple(val_x),
            # y
            (
                user_line["user_decision"],
                user_line["user_bet_val"] * 100,
                user_line["user_decision"] == user_line['question']["ai_is_correct"],
                user_line['question']["ai_is_correct"],
            ))
        )
    return out

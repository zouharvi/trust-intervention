#!/usr/bin/env python3
from collections import defaultdict
import json
def load_data(filename):
    data = [json.loads(x) for x in open(filename, "r")]
    user_data = defaultdict(list)
    queue_data = defaultdict(list)

    for datum in data:
        user_data[datum['url_data']['prolific_id']].append(datum)
        queue_data[datum['url_data']["prolific_queue_name"]].append(datum)


    queue_user_data = defaultdict(lambda: defaultdict(list))
    for study, data in queue_data.items():
        for datum in data:
            queue_user_data[study][datum['url_data']['prolific_id']].append(datum)

    ## filtering conditions


    # data_clean = []

    # removed = 0
    # for user_v in prolific_data:
    #     corrrect_count = 0
    #     total_count = 0
    #     for line_k, line_v in user_v.items():
    #         if type(line_v) == dict:
    #             line_v["question"] = question_data[f"q{line_k}"]
    #             del line_v["saw_passage2"]
    #             corrrect_count += (line_v["correct"]) * 1
    #             total_count += 1

    #     if corrrect_count >= 20:
    #         data_clean.append(user_v)
    #     else:
    #         removed += 1

    # print(f"removed {removed} from total of {len(prolific_data)}")

    return data, user_data, queue_user_data


def load_split_data(data, type="flat" ):
    import sklearn.model_selection

    prolific_data = [
        (
            featurize_user_lines_simple(user)
            if simple else
            featurize_user_lines(user)
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


def get_y_multi(line, features=[1, 2]):
    return [str([y[feature] for feature in features]) for x, y in line]


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
    user_features = []
    labels = []
    prior_confusion_matrix = []
    
    for datum in user_data:


        user_features.append((
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

        ))
        prior_confusion_matrix.append((
            # Tx / Fx
            datum['question']["ai_is_correct"],
            # xP / xN
            datum["user_decision"] == "agree",
        ))

        labels.append((
            datum["user_decision"] == "agree",
            datum['question']["ai_is_correct"],
            datum["user_bet_val"]
        ))

    return user_features, labels
    










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

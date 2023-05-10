#!/usr/bin/env python3
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import json
def load_data(user_data, question_data):
    import json
    # import pdb
    # pdb.set_trace() 
    prolific_data = [
        {k: json.loads(v) for k, v in json.loads(l).items()}
        for l in open(f"data/{user_data}", "r").readlines()
    ]

    question_data = json.load(open(f"data/{question_data}", "r"))

    data_clean = []

    removed = 0
    for user_v in prolific_data:
        corrrect_count = 0
        total_count = 0
        for line_k, line_v in user_v.items():
            if type(line_v) == dict:
                line_v["question"] = question_data[f"q{line_k}"]
                del line_v["saw_passage2"]
                corrrect_count += (line_v["correct"])*1
                total_count += 1

        if corrrect_count >= 20:
            data_clean.append(user_v)
        else:
            removed += 1

    print(f"removed {removed} from total of {len(prolific_data)}")

    return data_clean

def load_data_frame(user_data, question_data):
    ## Convert data into a pandas dataframe
    import json
    prolific_data = load_data(user_data, question_data)
    prolific_data = [
        featurize_user_lines_(user)
        for user in prolific_data
    ]

    all_data = flatten_(prolific_data)

    all_data = get_x_y(all_data)
    all_data = pd.DataFrame(all_data, columns=FEATURE_NAMES + PREDICTOR_NAMES  +["user_id"])


    # md = smf.mixedlm("agree ~  int_before + int_inside + int_after", all_data, groups=all_data["user_id"])
    # mdf = md.fit(method=["lbfgs"])
    # print(mdf.summary())
    return all_data

def load_split_data():
    import sklearn.model_selection

    prolific_data = load_data()
    prolific_data = [
        featurize_user_lines(user)
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

def flatten_(data):
    return [list(l) + [u_id] for u_id, u in enumerate(data) for l in u]

def get_x_y(line): 
    return [list(x) + list(y) + list([z]) for x, y, z in line]

def get_x(line):
    return [x for x, y in line]

def get_y(line, feature=0):
    return [y[feature] for x, y in line]

def get_y_multi(line, features=[1,2]):
    return [str([y[feature] for feature in features]) for x, y in line]

FEATURE_NAMES = [
    "model_confidence",
    "avg_prev_passage_show",
    "avg_prev_TP",
    "avg_prev_FP",
    "avg_prev_TN",
    "avg_prev_FN",
    # "time",
    "int_before", "int_inside", "int_after",
    "beginning_question",
]

PREDICTOR_NAMES = ["saw_passage1", "agree", "correct"]

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
                float(line["question"]["conf"].removesuffix("%"))/100,
                # average of previous passages
                _avg_empty(prior_passage_saw),
                # average previoux TP
                _avg_empty([x and y for x, y in prior_confusion_matrix]),
                # average previoux FP
                _avg_empty([not x and y for x, y in prior_confusion_matrix]),
                # average previoux TN
                _avg_empty(
                    [not x and not y for x, y in prior_confusion_matrix]),
                # average previoux FN
                _avg_empty([x and not y for x, y in prior_confusion_matrix]),
                # time
                # line["time"],
                # intervention location
                line["q_no"] < 14, line["q_no"] >= 14 and line["q_no"] <= 18, line["q_no"] > 18,
                # question number
                # line["q_no"],

                line["q_no"] < 5
            ),

            # TARGET
            (
                # trust
                line["saw_passage1"],
                # trust
                line["response"] == "agree",
                # success
                (line["response"] == "agree") == line["correct"],
            )
        ))
        prior_passage_saw.append(line["saw_passage1"])
        prior_confusion_matrix.append((
            # Tx, Fx
            (line["response"] == "agree") == line["correct"],
            # xP, xN
            line["response"] == "agree",
        ))

def featurize_user_lines_(user):
    out = []
    prior_passage_saw = []
    prior_confusion_matrix = []
    # print(user.values())
    for key, line in user.items():
        if key in ["exit_screen", "Reward"]:
            continue

        if type(line) != dict:
            line = json.loads(line)
        try:
            out.append((
                # SOURCE
                (
                    # model confidence
                    float(line["question"]["conf"].removesuffix("%"))/100 if "question" in line else 0.0,
                    # average of previous passages
                    _avg_empty(prior_passage_saw),
                    # average previoux TP
                    _avg_empty([x and y for x, y in prior_confusion_matrix]),
                    # average previoux FP
                    _avg_empty([not x and y for x, y in prior_confusion_matrix]),
                    # average previoux TN
                    _avg_empty(
                        [not x and not y for x, y in prior_confusion_matrix]),
                    # average previoux FN
                    _avg_empty([x and not y for x, y in prior_confusion_matrix]),
                    # time
                    # line["time"],
                    # intervention location
                    float(line["q_no"] < 14), float(line["q_no"] >= 14) and float(line["q_no"] <= 18), float(line["q_no"] > 18),
                    # question number
                    # line["q_no"],

                    float(line["q_no"] < 5)
                ),

                # TARGET
                (
                    # trust
                    float(line["saw_passage1"] if "saw_passage1" in line else False),
                    # trust
                    float(line["response"] == "agree" or line["response"] == "know_ans"),
                    # success
                    float(line["response"] == "know_ans" or (line["response"] == "agree") == line["correct"]),
                )
            ))
        except:
            import pdb; pdb.set_trace()
        if line["response"] == "know_ans":
            continue
        prior_passage_saw.append(line["saw_passage1"])
        prior_confusion_matrix.append((
            # Tx, Fx
            (line["response"] == "agree") == line["correct"],
            # xP, xN
            line["response"] == "agree",
        ))

    
    # print(len(out))
    return out
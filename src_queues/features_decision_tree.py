#!/usr/bin/env python3

import utils
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, plot_tree
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error
import matplotlib.pyplot as plt
import numpy as np

data_train, data_test = utils.load_split_data(
    path="data/collected_users.jsonl",
    queue=["control_long", "intervention_ci_long"],
    question_classes=False
)
data_test = utils.flatten(data_test)
data_train = utils.flatten(data_train)

my_metric_f1 = lambda *x: f1_score(*x, pos_label=True)

def eval_dt_classification(data_train_x, data_train_y, data_test_x, data_test_y):
    model = DecisionTreeClassifier()
    model.fit(data_train_x, data_train_y)
    data_test_y_pred = model.predict(data_test_x)
    acc = accuracy_score(data_test_y_pred, data_test_y)
    f1 = my_metric_f1(data_test_y_pred, data_test_y)
    return acc, f1


def eval_dt_regression(data_train_x, data_train_y, data_test_x, data_test_y):
    model = DecisionTreeRegressor(criterion="absolute_error", random_state=0, max_depth=5)
    model.fit(data_train_x, data_train_y)
    data_test_y_pred = model.predict(data_test_x)
    mae = mean_absolute_error(data_test_y_pred, data_test_y)
    print(model.feature_importances_)
    plot_tree(
        model,
        max_depth=3
    )
    plt.tight_layout()
    plt.savefig("computed/figures/dt.pdf")
    plt.show()
    return mae


for feature, feature_type in [
    # (0, "classification"),
    (1, "regression"),
    # (2, "classification"),
    # (3, "classification")
]:
    data_train_x = utils.get_x(data_train)
    data_train_y = utils.get_y(data_train, feature=feature)
    data_test_x = utils.get_x(data_test)
    data_test_y = utils.get_y(data_test, feature=feature)

    if feature_type == "classification":
        acc, f1 = eval_dt_classification(
            data_train_x, data_train_y,
            data_test_x, data_test_y
        )
        print(
            (
                "\\accfcell{" +
                f"{acc:.1%}".replace("%", "\\%") +
                "}{" +
                f"{f1:.1%}".replace("%", "\\%") +
                "}"
            ),
        )
    elif feature_type == "regression":
        mae = eval_dt_regression(
            data_train_x, data_train_y,
            data_test_x, data_test_y
        )
        print(
            (
                f"{mae:.1f}\\mathcent"
            ),
        )
    else:
        raise Exception()

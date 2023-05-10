#!/usr/bin/env python3

import utils
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, f1_score

data_train, data_test = utils.load_split_data()
data_test = utils.flatten(data_test)
data_train = utils.flatten(data_train)

my_metric_f1 = lambda *x: f1_score(*x, pos_label="[True]")
my_metric_acc = lambda *x: accuracy_score(*x)


def eval_constant_baseline(data_train_x, data_train_y, data_test_x, data_test_y):
    # force positive class
    acc = my_metric_f1(['[True]'] * len(data_test_x), data_test_y)
    f1 = my_metric_f1(['[True]'] * len(data_test_x), data_test_y)
    return acc, f1


def eval_logistic_regression(data_train_x, data_train_y, data_test_x, data_test_y):
    model = LogisticRegression()
    model.fit(data_train_x, data_train_y)
    data_test_y_pred = model.predict(data_test_x)
    acc = my_metric_acc(data_test_y_pred, data_test_y)
    f1 = my_metric_f1(data_test_y_pred, data_test_y)
    return acc, f1


def eval_multilayer_perceptron(data_train_x, data_train_y, data_test_x, data_test_y):
    # model = MLPClassifier(hidden_layer_sizes=(10, 10, 10), max_iter=500)
    model = MLPClassifier(hidden_layer_sizes=(50, 50, 50), max_iter=500)
    model.fit(data_train_x, data_train_y)
    data_test_y_pred = model.predict(data_test_x)
    acc = my_metric_acc(data_test_y_pred, data_test_y)
    f1 = my_metric_f1(data_test_y_pred, data_test_y)
    return acc, f1


for model_name, model_fn in [
    ("Constant Baseline    ", eval_constant_baseline),
    ("Logistic Regression  ", eval_logistic_regression),
    ("Multilayer Perceptron", eval_multilayer_perceptron),
]:
    print(model_name, end=" & ")
    for features in [[0], [1], [2], [3]]:
        data_train_x = utils.get_x(data_train)
        data_train_y = utils.get_y_multi(data_train, features=features)
        data_test_x = utils.get_x(data_test)
        data_test_y = utils.get_y_multi(data_test, features=features)

        acc, f1 = model_fn(
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
            end=" & "
        )
    print("\\\\")


# joint
# for feature_i, feature_name in enumerate(utils.FEATURE_NAMES):
#     model = LogisticRegression()
#     data_train_x_local = [(x[feature_i],) for x in data_train_x]
#     model.fit(data_train_x_local, data_train_y)
#     print(f"{feature_name:>20}: {accuracy_score(model.predict(data_train_x_local), data_train_y):.2%}")

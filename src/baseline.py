#!/usr/bin/env python3

import utils
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
# from xgboost import XGBClassifier, XGBRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error
import numpy as np

data_train, data_test = utils.load_split_data(path="data/collected.jsonl", queue=["control_long", "intervention_ci_long"])
data_test = utils.flatten(data_test)
data_train = utils.flatten(data_train)

my_metric_f1 = lambda *x: f1_score(*x, pos_label=True)
LR_KWARGS = {"tol": 1e-6, "max_iter": 1000}

def eval_constant_classification(data_train_x, data_train_y, data_test_x, data_test_y):
    # force positive class
    acc = accuracy_score([True] * len(data_test_y), data_test_y)
    f1 = my_metric_f1([True] * len(data_test_y), data_test_y)
    return acc, f1

def eval_constant_regression(data_train_x, data_train_y, data_test_x, data_test_y):
    pred = np.average(data_train_y)
    mae = mean_absolute_error([pred]*len(data_test_y), data_test_y)
    return mae

def eval_lr_classification(data_train_x, data_train_y, data_test_x, data_test_y):
    model = LogisticRegression()
    model.fit(data_train_x, data_train_y)
    data_test_y_pred = model.predict(data_test_x)
    acc = accuracy_score(data_test_y_pred, data_test_y)
    f1 = my_metric_f1(data_test_y_pred, data_test_y)
    return acc, f1

def eval_lr_regression(data_train_x, data_train_y, data_test_x, data_test_y):
    model = LinearRegression()
    model.fit(data_train_x, data_train_y)
    data_test_y_pred = model.predict(data_test_x)
    mae = mean_absolute_error(data_test_y_pred, data_test_y)
    return mae

def eval_rf_classification(data_train_x, data_train_y, data_test_x, data_test_y):
    model = RandomForestClassifier(n_estimators=1000)
    model.fit(data_train_x, data_train_y)
    data_test_y_pred = model.predict(data_test_x)
    acc = accuracy_score(data_test_y_pred, data_test_y)
    f1 = my_metric_f1(data_test_y_pred, data_test_y)
    return acc, f1

def eval_rf_regression(data_train_x, data_train_y, data_test_x, data_test_y):
    model = RandomForestRegressor(n_estimators=1000)
    model.fit(data_train_x, data_train_y)
    data_test_y_pred = model.predict(data_test_x)
    mae = mean_absolute_error(data_test_y_pred, data_test_y)
    return mae

def eval_mlp_classification(data_train_x, data_train_y, data_test_x, data_test_y):
    model = MLPClassifier(hidden_layer_sizes=(50, 50), max_iter=50000, tol=1e-6)
    model.fit(data_train_x, data_train_y)
    data_test_y_pred = model.predict(data_test_x)
    acc = accuracy_score(data_test_y_pred, data_test_y)
    f1 = my_metric_f1(data_test_y_pred, data_test_y)
    return acc, f1

def eval_mlp_regression(data_train_x, data_train_y, data_test_x, data_test_y):
    model = MLPRegressor(hidden_layer_sizes=(50, 50), max_iter=50000, tol=1e-6)
    model.fit(data_train_x, data_train_y)
    data_test_y_pred = model.predict(data_test_x)
    mae = mean_absolute_error(data_test_y_pred, data_test_y)
    return mae

for model_name, (model_fn_classification, model_fn_regression) in [
    ("Constant Baseline    ", (eval_constant_classification, eval_constant_regression)),
    ("Linear Regression    ", (eval_lr_classification, eval_lr_regression)),
    ("Random Forest        ", (eval_rf_classification, eval_rf_regression)),
    ("Multilayer Perceptron", (eval_mlp_classification, eval_mlp_regression)),
]:
    print(model_name, end=" & ")
    for feature, feature_type in [
        (0, "classification"),
        (1, "regression"),
        (2, "classification"),
        (3, "classification")
    ]:
        data_train_x = utils.get_x(data_train)
        data_train_y = utils.get_y(data_train, feature=feature)
        data_test_x = utils.get_x(data_test)
        data_test_y = utils.get_y(data_test, feature=feature)

        if feature_type == "classification":
            acc, f1 = model_fn_classification(
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
        elif feature_type == "regression":
            mae = model_fn_regression(
                data_train_x, data_train_y,
                data_test_x, data_test_y
            )
            print(
                (
                    f"{mae:.1f}\\mathcent"
                ),
                end=" & "
            )
        else:
            raise Exception()
    print("\\\\")
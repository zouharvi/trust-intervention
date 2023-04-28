#!/usr/bin/env python3

import utils
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, f1_score

data_train, data_test = utils.load_split_data()
data_test = utils.flatten(data_test)
data_train = utils.flatten(data_train)

my_metric = lambda *x: f1_score(*x, pos_label="[True]")

for features in [[0], [1], [2]]:
    print("features", features)
    data_train_x = utils.get_x(data_train)
    data_train_y = utils.get_y_multi(data_train, features=features)
    data_test_x = utils.get_x(data_test)
    data_test_y = utils.get_y_multi(data_test, features=features)

    # model_dummy = DummyClassifier(strategy="prior", constant="[False]")
    # force positive class
    print(
        f"Dummy acc (train/test):  ",
        f"{my_metric(['[True]']*len(data_train_x), data_train_y):.1%} / {my_metric(['[True]']*len(data_test_x), data_test_y):.1%}"
    )

    model = LogisticRegression()
    model.fit(data_train_x, data_train_y)
    print(
        f"Full LR acc (train/test):",
        f"{my_metric(model.predict(data_train_x), data_train_y):.1%} / {my_metric(model.predict(data_test_x), data_test_y):.1%}"
    )

    # model = MLPClassifier(hidden_layer_sizes=(10, 10, 10), max_iter=500)
    model = MLPClassifier(hidden_layer_sizes=(50, 50, 50), max_iter=400)
    model.fit(data_train_x, data_train_y)
    print(
        f"MLP acc (train/test):    ",
        f"{my_metric(model.predict(data_train_x), data_train_y):.1%} / {my_metric(model.predict(data_test_x), data_test_y):.1%}"
    )

    print("\n")
    # for feature_i, feature_name in enumerate(utils.FEATURE_NAMES):
    #     model = LogisticRegression()
    #     data_train_x_local = [(x[feature_i],) for x in data_train_x]
    #     model.fit(data_train_x_local, data_train_y)
    #     print(f"{feature_name:>20}: {accuracy_score(model.predict(data_train_x_local), data_train_y):.2%}")

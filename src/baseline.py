#!/usr/bin/env python3

import utils
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
import argparse
import os
import sys


#argument parsing
parser = argparse.ArgumentParser(description='run baseline models')
parser.add_argument('--data', type=str, default="data", help='path to data directory')

args = parser.parse_args()

data, user_data, queue_user_data = utils.load_data(args.data)
# how do we want to split???
#split_data_randomly
features_labels_per_user = []
for user, datum in user_data.items(): 
    user_features, labels = utils.featurize_datum(datum)
    features_labels_per_user.append((user_features, labels))

#split_data_by_user
train_features = []
train_labels = []
test_features = []
test_labels = []
for user_features, labels in features_labels_per_user:
    if np.random.rand() < 0.8:
        train_features.append(user_features)
        train_labels.append(labels)
    else:
        test_features.append(user_features)
        test_labels.append(labels)

import pdb
pdb.set_trace()

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
    import pdb; pdb.set_trace()

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

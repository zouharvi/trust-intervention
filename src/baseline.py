#!/usr/bin/env python3

import utils
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score

data_train, data_test = utils.load_split_data()
data_test = utils.flatten(data_test)
data_train = utils.flatten(data_train)

for features in [[0], [1], [2]]:
    print("features", features)
    data_train_x = utils.get_x(data_train)
    data_train_y = utils.get_y_multi(data_train, features=features)
    data_test_x = utils.get_x(data_test)
    data_test_y = utils.get_y_multi(data_test, features=features)

    model_dummy = DummyClassifier(strategy="most_frequent")
    model_dummy.fit(data_train_x, data_train_y)
    print(f"Dummy acc (train): {accuracy_score(model_dummy.predict(data_train_x), data_train_y):.2%}")
    print(f"Dummy acc (test): {accuracy_score(model_dummy.predict(data_test_x), data_test_y):.2%}")

    model = LogisticRegression()
    model.fit(data_train_x, data_train_y)
    print(f"Full LR acc (train): {accuracy_score(model.predict(data_train_x), data_train_y):.2%}")
    print(f"Full LR acc (test): {accuracy_score(model.predict(data_test_x), data_test_y):.2%}")

    print("\n")
    # for feature_i, feature_name in enumerate(utils.FEATURE_NAMES):
    #     model = LogisticRegression()
    #     data_train_x_local = [(x[feature_i],) for x in data_train_x]
    #     model.fit(data_train_x_local, data_train_y)
    #     print(f"{feature_name:>20}: {accuracy_score(model.predict(data_train_x_local), data_train_y):.2%}")

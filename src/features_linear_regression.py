#!/usr/bin/env python3

import utils
from statsmodels.regression.linear_model import OLS

data_train, data_test = utils.load_split_data(
    path="data/collected.jsonl",
    queue=["control_long", "intervention_ci_long"],
    question_classes=False
)
data_test = utils.flatten(data_test)
data_train = utils.flatten(data_train)


data_train_x = utils.get_x(data_train)
data_train_y = utils.get_y(data_train, feature=1)
data_test_x = utils.get_x(data_test)
data_test_y = utils.get_y(data_test, feature=1)

for i in range(len(data_train_x[0])):
    print("feature", i)
    model = OLS(data_train_y, [[x[i]] for x in data_train_x]).fit()
    print(model.rsquared)
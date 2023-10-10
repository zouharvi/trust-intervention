#!/usr/bin/env python3

import utils
from sklearn.metrics import mean_absolute_error
from sklearn.neural_network import MLPRegressor
import numpy as np
import shap

data_train, data_test = utils.load_split_data(
    path="data/collected_users.jsonl",
    queue=["control_long", "intervention_ci_long"],
    question_classes=False
)
data_test = utils.flatten(data_test)
data_train = utils.flatten(data_train)


data_train_x = utils.get_x(data_train)
data_train_y = utils.get_y(data_train, feature=1)
data_test_x = utils.get_x(data_test)
data_test_y = utils.get_y(data_test, feature=1)

model = MLPRegressor(
    hidden_layer_sizes=(50, 50), max_iter=50000, tol=1e-6
)
model.fit(data_train_x, data_train_y)
# data_test_y_pred = model.predict(data_test_x)
# mae = mean_absolute_error(data_test_y_pred, data_test_y)
# print(mae)

data_train_x = np.array(data_train_x[:1000])
data_test_x = np.array(data_test_x[:50])

explainer = shap.KernelExplainer(model.predict, data_train_x)
shap_values = explainer.shap_values(data_test_x, nsamples=100)
print(shap_values.shape)
print(np.average(np.abs(shap_values), axis=0))
shap.summary_plot(
    shap_values,data_test_x,
    feature_names=[
        "avg_prior_bet",
        "avg_TP", "avg_FP", "avg_TN", "avg_FN",
        "AI_conf", "question_pos"
    ]
)

from utils import load_data, load_data_frame
import matplotlib.pyplot as plt
from smoother import savitzky_golay

data_intervention = load_data_frame("prolific_int_general.jsonl", "int_general.json")

saw_passage_intervention = data_intervention.groupby("user_id").apply(lambda x: x)["saw_passage1"].to_numpy().reshape(-1, 30).mean(0)



data_control = load_data_frame("prolific_control_2_data.jsonl", "int_control.json")

saw_passage_control = data_control.groupby("user_id").apply(lambda x: x)["saw_passage1"].to_numpy().reshape(-1, 30).mean(0)

saw_passage_intervention -= saw_passage_intervention.mean()
saw_passage_control -= saw_passage_control.mean()
saw_passage_control = savitzky_golay(saw_passage_control, 5, 3)
saw_passage_intervention = savitzky_golay(saw_passage_intervention, 5, 3)
plt.plot(saw_passage_intervention)
plt.plot(saw_passage_control)
plt.savefig("intervention_control_smooth.png")



# plt.plot(saw_passage_intervention)
# plt.savefig("intervention.png")


# plt.plot(saw_passage_control)
# plt.savefig("control.png")
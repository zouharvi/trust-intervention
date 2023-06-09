#!/usr/bin/env python3

import requests
import json
import argparse
from secret import API_TOKEN
import time
from collections import defaultdict
import numpy as np

messages = {
    'exit_screen': "You exited the screen more than three times and this was explicitly forbidden in the instructions.",
    "too_fast": "You completed the task too quickly indicated you didn't attempt each question seriously.",
    "no_code": "You didn't complete the experiments and did not have the final code",
    "too_slow": "You took too long to complete the task indicating external help",
}


def get_submissions(study_id):
    r = requests.get(
        f"https://api.prolific.co/api/v1/studies/{study_id}/submissions/",
        params={"state": "AWAITING REVIEW"},
        headers={"Authorization": f"Token {API_TOKEN}"}
    )
    if not r.ok:
        exit("Unable to complete an important request (fetching submissions).")
    d = r.json()["results"]
    return d


def get_studies():
    r = requests.get(
        "https://api.prolific.co/api/v1/studies/",
        params={"state": "AWAITING REVIEW"},
        headers={"Authorization": f"Token {API_TOKEN}"}
    )
    if not r.ok:
        exit("Unable to complete an important request (fetching studies).")
    d = r.json()["results"]
    return d


def name_check():
    r = requests.get(
        "https://api.prolific.co/api/v1/users/me/",
        headers={"Authorization": f"Token {API_TOKEN}"}
    )

    if not r.ok:
        exit("Unable to make test API call, likely the API code is not working.")
    d = r.json()
    input(f"Is your name {d['name']}? [ctrl-c] if not, [enter] if yes.")


def reject_submission(submission_id, participant_id, message, rejection_category):
    if args.dry_run:
        print(
            f"Not continuing because of --dry-run but would reject"
            f"{submission_id} of {participant_id}"
        )
        return
    
    if rejection_category not in ["TOO_QUICKLY", "TOO_SLOWLY" ,"FAILED_INSTRUCTIONS", "INCOMP_LONGITUDINAL", "FAILED_CHECK" ,"LOW_EFFORT",
                       "MALINGERING" ,"NO_CODE", "BAD_CODE", "NO_DATA", "UNSUPP_DEVICE", "OTHER"]:
        print(rejection_category)
    r = requests.post(
        f"https://api.prolific.co/api/v1/submissions/{submission_id}/transition/",
        headers={"Authorization": f"Token {API_TOKEN}"},

        json={
            "action": "REJECT",
            "message": message,
            "rejection_category": rejection_category
        }
    )
    if not r.ok:
        exit(
            f"Failed rejection of {submission_id} of participant {participant_id}"
        )
    d = r.json()
    print(f'status: {d["status"]}, participant: {d["participant"]}')


def approve_submission(submission_id, participant_id):
    if args.dry_run:
        print(
            f"Not continuing because of --dry-run but would approve {submission_id} of {participant_id}"
        )
        return
    r = requests.post(
        f"https://api.prolific.co/api/v1/submissions/{submission_id}/transition/",
        headers={"Authorization": f"Token {API_TOKEN}"},
        json={
            "action": "APPROVE",
        }
    )
    if not r.ok:
        exit(
            f"Failed approval of {submission_id} of participant {participant_id}"
        )
    d = r.json()
    print(f'status: {d["status"]}, participant: {d["participant"]}')


def setup_bonuses(approved_participants, study_id):
    if args.dry_run:
        print(
            "Not continuing because of --dry-run but would set up the following csv bonuses"
        )
        print("\\n".join(
            [f"{x['worker_id']},{x['bonus']}" for x in approved_participants]
        ))
        return

    r = requests.post(
        f"https://api.prolific.co/api/v1/submissions/bonus-payments/",
        headers={"Authorization": f"Token {API_TOKEN}"},
        json={
            "study_id": study_id,
            "csv_bonuses": "\n".join([f"{x['id']},{x['bonus']}" for x in approved_participants])
        }
    )
    if not r.ok:
        exit("Failed to set up bonus payment " + r.content.decode())
    d = r.json()
    print("Set up bonus payment with the following response", d)
    return d["id"]


def pay_bonuses(bonus_id):
    if args.dry_run:
        print(
            f"Not continuing because of --dry-run but would pay the id {bonus_id}")
        return

    r = requests.post(
        f"https://api.prolific.co/api/v1/bulk-bonus-payments/{bonus_id}/pay/",
        headers={"Authorization": f"Token {API_TOKEN}"},
    )
    if not r.ok:
        exit("Failed to pay bonus payment " + r.content.decode())
    d = r.json()
    print("Paid the bonus with the following response", d)


args = argparse.ArgumentParser()
args.add_argument(
    "--control-file", "-cf",
    default="secret/control_prolific.jsonl"
)
args.add_argument("--dry-run", "-dr", action="store_true")
args = args.parse_args()

control_data = [json.loads(x) for x in open(args.control_file, "r")]

user_data = defaultdict(list)
study_data = defaultdict(list)
for idx,datum in enumerate(control_data):
    try:
        if 'prolific_id' not in datum['url_data']:
            continue
        user_data[datum['url_data']['prolific_id']].append(datum)
        study_data[datum['url_data']['study_id']].append(datum)
    except KeyError:
        print(f"Failed on {idx}")
        continue
study_user_data = defaultdict(lambda: defaultdict(list))
for study, data in study_data.items():
    for datum in data:
        study_user_data[study][datum['url_data']['prolific_id']].append(datum)

test_users = []
for user, datum in user_data.items():

    # print(len(datum))
    if datum[0]['url_data']["prolific_queue_name"] == "discept_pilot_0":
        print(f"Exclude user {user} because they are in the pilot")
        test_users.append(user)
        # print(f"The user {user} has {len(datum)} entries. Please manually check this!")
        # if user == "63172692591f6b7c1b94af3a":
        #     continue
    if len(datum) not in [ 30, 60]:
        print(f"The user {user} has {len(datum)} entries. Please manually check this!")

    


    if "qno" in datum[0]:
        # we sort
        assert False

for uu in ["604f684950227bd07a37376d", "63ea52b8342eff8b95ef0f95", "5dcf2c967beb290802f26b45"]:
    if uu in user_data:
        user_data.pop(uu)

for user in test_users:
    user_data.pop(user)

name_check()

d_studies = get_studies()
d_studies = [
    x for x in d_studies
    if x["id"] in study_data
]
if len(d_studies) < 1:
    exit(f"Found no studies")

print(f"Found the following studies")
for d_study in d_studies:
    print(d_study["name"], d_study["id"], d_study["internal_name"])
    # if d_study["id"] != "645e327ea266fd4337abb412":
    #     continue


    # if d_study["id"] != "6460f2d2af2bdcc493e162db":
    #     continue

    d_submissions = get_submissions(d_study['id'])
    d_submissions_awaiting = [
        x for x in d_submissions
        if x["status"] == "AWAITING REVIEW"
    ]

    no_code_submissions = [
        x for x in d_submissions
        if  x["study_code"] is None or x["study_code"] != "C8RJ1YCV"
    ]

    code_submissions = [
        x for x in d_submissions
        if  x["study_code"] is not None and x["study_code"] == "C8RJ1YCV"
    ]


    print(f"Found {len(no_code_submissions)} submissions without code")

    print(
        f"Fetched {len(d_submissions)} submissions out of which {len(d_submissions_awaiting)} are awaiting review")

    pid_to_sid = {x["participant_id"]: x["id"] for x in d_submissions}
    pid_to_sid_awaiting = {
        x["participant_id"]: x["id"]
        for x in d_submissions_awaiting
    }


    pid_to_sid_no_code = {
        x["participant_id"]: x["id"]
        for x in no_code_submissions
    }



    users_waiting_to_be_approved = []
    users_waiting_to_be_rejected = []

    current_study_data = study_user_data[d_study['id']]
    for user, datum in current_study_data.items():
        if user not in pid_to_sid_awaiting:
            if user not in pid_to_sid:
                exit(
                    f"Could not find entry for prolific participant id {user}"
                )
            else:
                print(
                    f"The prolific participant {user} has already been approved, skipping.\n",
                    "Please don't include them in the control file so that nobody gets paid twice."
                )
        else:


            # Rejection criteria exit screen > 3
            exit_screen = sum([int(d['count_exited_page']) for d in datum]) > 3
            ## Rejection criteria too fast
            too_fast = np.mean([sum([t for t in d['times'].values()]) for d in datum]) < 3000
            too_slow = np.mean([sum([t for t in d['times'].values()]) for d in datum]) < 3000
            attempt = len(datum)

            if user in pid_to_sid_no_code:
                users_waiting_to_be_rejected.append({'id':user, 'reason':messages['no_code'], "rejection_category":"NO_CODE", "session_id":datum[0]['url_data']['session_id']})
            elif exit_screen:
                users_waiting_to_be_rejected.append({'id':user, 'reason':messages['exit_screen'], "rejection_category":"FAILED_INSTRUCTIONS", "session_id":datum[0]['url_data']['session_id']})
            elif too_fast:
                users_waiting_to_be_rejected.append({
                    'id': user, 'reason': messages['too_fast'], "rejection_category": "TOO_QUICKLY", "session_id": datum[0]['url_data']['session_id']
                })
            elif too_slow:
                users_waiting_to_be_rejected.append({
                    'id': user, 'reason': messages['too_slow'], "rejection_category": "TOO_SLOWLY", "session_id": datum[0]['url_data']['session_id']
                })
            else:
                # Accept
                users_waiting_to_be_approved.append({
                    "id": user, "bonus": datum[-1]['user_balance'], "session_id": datum[0]['url_data']['session_id']
                })
                print(f"Will approve {user} with bonus {datum[-1]['user_balance']}")

    print(f"In study {d_study['id']} we have {len(users_waiting_to_be_approved)} participants to approve and {len(users_waiting_to_be_rejected)} to reject")

    print(
        f"Will reject {len(users_waiting_to_be_rejected)} participants"
    )
    print(
        f"Will approve {len(users_waiting_to_be_approved)} participants "
        f"and give them {sum([float(x['bonus']) for x in users_waiting_to_be_approved ]):.2f} moneys in bonus (excluding base pay)"
    )
    input(f"If this looks good, press enter to continue.")
    # approve/reject
    for user in users_waiting_to_be_approved:
        # throttle because cancelling mid-payout is horrible (I wish there were transactions in Prolific API)
        time.sleep(1)

        approve_submission(user["session_id"], user["id"])
        with open("../data/local_ledger_approved.jsonl", "a") as f:
            f.write(json.dumps(user) + "\n")
        
        
    for user in users_waiting_to_be_rejected:
        # throttle because cancelling mid-payout is horrible (I wish there were transactions in Prolific API)
        time.sleep(1)

        reject_submission(user["session_id"], user["id"], user["reason"],  user["rejection_category"])
        with open("../data/local_ledger_rejected.jsonl", "a") as f:
            f.write(json.dumps(user) + "\n")

    if len(users_waiting_to_be_approved) > 0:
        bonus_id = setup_bonuses(users_waiting_to_be_approved, d_study["id"])
        pay_bonuses(bonus_id)

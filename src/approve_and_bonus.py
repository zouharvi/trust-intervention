#!/usr/bin/env python3

import requests
import json
import argparse
from secret import API_TOKEN
import time


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


def reject_submission(submission_id, participant_id):
    if args.dry_run:
        print(f"Not continuing because of --dry-run but would reject {submission_id} of {participant_id}")
        return
    r = requests.post(
        f"https://api.prolific.co/api/v1/submissions/{submission_id}/transition/",
        headers={"Authorization": f"Token {API_TOKEN}"},
        json={
            "action": "REJECT",
            "message": "The instructions stated that leaving the active window was not permitted during the experiment. You were additionally reminded of this after a few instances of this. Because this is crucial to the experiment design, we must reject your submission.",
            "rejection_category": "FAILED_INSTRUCTIONS"
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
        print(f"Not continuing because of --dry-run but would approve {submission_id} of {participant_id}")
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
        print("Not continuing because of --dry-run but would set up the following csv bonuses")
        print("\\n".join([f"{x['worker_id']},{x['bonus']}" for x in approved_participants]))
        return

    r = requests.post(
        f"https://api.prolific.co/api/v1/submissions/bonus-payments/",
        headers={"Authorization": f"Token {API_TOKEN}"},
        json={
            "study_id": study_id,
            "csv_bonuses": "\n".join([f"{x['worker_id']},{x['bonus']}" for x in approved_participants])
        }
    )
    if not r.ok:
        exit("Failed to set up bonus payment " + r.content.decode())
    d = r.json()
    print("Set up bonus payment with the following response", d)
    return d["id"]

def pay_bonuses(bonus_id):
    if args.dry_run:
        print(f"Not continuing because of --dry-run but would pay the id {bonus_id}")
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
if not all(control_data[0]["project_name"] == x["project_name"] for x in control_data):
    exit("Control file with multiple projects is not supported currently.")
if len(control_data) != len(set([x["worker_id"] for x in control_data])):
    exit("Duplicate worker ids in control file")

# name_check()

d_studies = get_studies()
d_studies = [
    x for x in d_studies
    if x["name"] == control_data[0]["project_name"]
]


if len(d_studies) != 1:
    exit(f"Expected exactly 1 project match, but found {len(d_studies)}.")

d_study = d_studies[0]
print(f"Found a matching project '{d_study['name']}' with id {d_study['id']}")
d_submissions = get_submissions(d_study['id'])
d_submissions_awaiting = [
    x for x in d_submissions
    if x["status"] == "AWAITING REVIEW"
]
print(f"Fetched {len(d_submissions)} submissions out of which {len(d_submissions_awaiting)} are awaiting review")

pid_to_sid = {x["participant_id"]: x["id"] for x in d_submissions}
pid_to_sid_awaiting = {
    x["participant_id"]: x["id"]
    for x in d_submissions_awaiting
}

# clean and filter users
# also match submission ids
control_data_clean = []
for user in control_data:
    if user["worker_id"] not in pid_to_sid_awaiting:
        if user["worker_id"] not in pid_to_sid:
            exit(
                f"Could not find entry for prolific participant id {user['worker_id']}"
            )
        else:
            print(
                f"The prolific participant {user['worker_id']} has already been approved, skipping.\nPlease don't include them in the control file so that nobody gets paid twice.")
    else:
        user["session_id"] = pid_to_sid_awaiting[user["worker_id"]]
        control_data_clean.append(user)

print(
    f"Will reject {len([x for x in control_data_clean if not x['approve']])} participants"
)
print(
    f"Will approve {len([x for x in control_data_clean if x['approve']])} participants "
    f"and give them {sum([float(x['bonus']) for x in control_data_clean if x['approve']]):.2f} moneys in bonus (excluding base pay)"
)

# approve/reject
for user in control_data_clean:
    # throttle because cancelling mid-payout is horrible (I wish there were transactions in Prolific API)
    time.sleep(1)
    if user["approve"]:
        approve_submission(user["session_id"], user["worker_id"])
    else:
        reject_submission(user["session_id"], user["worker_id"])

approved_participants = [x for x in control_data_clean if x['approve']]
bonus_id = setup_bonuses(approved_participants, d_study["id"])
pay_bonuses(bonus_id)
import requests
import csv

import yaml
import pathlib


def get_github_token(secrets_file):
    ### Get github token from secrets file

    with pathlib.Path(secrets_file).open() as f:
        file_contents = yaml.safe_load(f) or {}
        github_token = file_contents.get("github_token")
        if github_token:
            return github_token

    raise ValueError(
        f"Missing required 'github_token' in secrets file: {secrets_file}"
    )
def get_auth_headers():
    ### Get the authorisation headers required for GitHub access

    headers = {"Authorization": f"Bearer {get_github_token('secrets.yml')}"}
    return {"headers": headers}


def get_list_of_workflows(org: str, repo: str):
    ### Gets a list of workflows from the given repo

    url = f"https://api.github.com/repos/{org}/{repo}/actions/runs"

    kwargs = get_auth_headers()

    return requests.get(url, **kwargs)


def get_one_workflow_info(org: str, repo: str, workflow_run: str):
    url = f"https://api.github.com/repos/{org}/{repo}/actions/runs/{workflow_run}"

    kwargs = get_auth_headers()
    return requests.get(url, **kwargs)


def get_workflow_runtime_info(org: str, repo: str, workflow_run: str):
    ### Extract the timing information from a single workflow

    url = (
        f"https://api.github.com/repos/{org}/{repo}/actions/runs/{workflow_run}/timing"
    )

    kwargs = get_auth_headers()

    return requests.get(url, **kwargs)


def make_csv_output(data):
    ### Output the data to CSV format

    if not data:
        print("No workflow timing data available; skipping CSV output.")
        return
    with open("output.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(data[0].keys()))
        w.writeheader()
        w.writerows(data)


if __name__ == "__main__":
    auth_headers = get_auth_headers()

    org_name = "green-actions"
    repo_name = "green-actions"

    workflows = get_list_of_workflows(org_name, repo_name)

    output_dict = []

    wf_data = workflows.json()
    print(workflows)
    print(wf_data["total_count"])
    for wf_run in wf_data["workflow_runs"]:
        tmp_output = {
            "workflow_name": wf_run["name"],
            "branch": wf_run["head_branch"],
            "start_time": wf_run["run_started_at"],
        }
        timing_info = get_workflow_runtime_info(
            org_name, repo_name, wf_run["id"]
        ).json()

        if "run_duration_ms" in timing_info.keys():
            tmp_output["duration"] = timing_info["run_duration_ms"]
            output_dict.append(tmp_output)
        else:
            print("No timing")

    make_csv_output(output_dict)

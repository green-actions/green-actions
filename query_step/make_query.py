import requests
import csv


def get_github_token(secrets_file):
    ### Get github token from secrets file
    github_token = ""
    import yaml
    from pathlib import Path
    with Path(secrets_file).open() as f:
        file_contents = yaml.safe_load(f)
        if "github_token" in file_contents.keys():
            return file_contents["github_token"]


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
    
    url = f"https://api.github.com/repos/{org}/{repo}/actions/runs/{workflow_run}/timing"
    
    kwargs = get_auth_headers()

    return requests.get(url, **kwargs)

def make_csv_output(data, out_name):
    ### Output the data to CSV format

    with open(out_name, "w", newline='') as f:
        w = csv.DictWriter(f,list(data[0].keys()))
        w.writeheader()
        w.writerows(data)
        

def run_one_repo(org_name: str, repo_name: str, output_name: str):

    # Get the workflows that have been called in this repo
    workflows = get_list_of_workflows(org_name, repo_name)

    # Collect information from issues here
    output_dict = []

    wf_data = workflows.json()

    print(f"Running over {len(wf_data['workflow_runs'])} workflows")
    
    # Loop over each workflow
    for wf_run in wf_data["workflow_runs"]:
        # A temp dict to store this workflow's information
        tmp_output = {}
        # Store base info
        tmp_output["workflow_name"] = wf_run["name"]
        tmp_output["branch"] = wf_run["head_branch"]
        tmp_output["start_time"] = wf_run["run_started_at"]

        # Get timing info for this workflow
        timing_info = get_workflow_runtime_info(org_name,repo_name,wf_run["id"]).json()

        # If there is timing info, save it to the dictionary and append that to our output
        if "run_duration_ms" in timing_info.keys():
            tmp_output["duration"] = timing_info["run_duration_ms"]
            output_dict.append(tmp_output)
        else:
            print(f"No timing information available for {wf_run['name']} run number {wf_run['id']}")

    # Turn this into an output
    make_csv_output(output_dict, output_name)

        
if __name__ == "__main__":

    # The org and repo names to query
    org_name = "green-actions"
    repo_name = "green-actions"

    out_name = "test_out.csv"

    run_one_repo(org_name, repo_name, out_name)

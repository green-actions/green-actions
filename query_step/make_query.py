import requests



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

    url = f"https://api.github.com/repos/{org}/{repo}/actions/runs/{workflow_run}/timing"
    url = f"https://api.github.com/repos/{org}/{repo}/actions/runs/{workflow_run}/timing"
    print(url)
    
    kwargs = get_auth_headers()

    return requests.get(url, **kwargs)


if __name__ == "__main__":
    
    auth_headers = get_auth_headers()

    org_name = "green-actions"
    repo_name = "green-actions"
    
    workflows = get_list_of_workflows(org_name, repo_name)

    wf_data = workflows.json()
    print(workflows)
    print(wf_data["total_count"])
    for wf_run in wf_data["workflow_runs"]:
        print(wf_run["name"],wf_run["run_number"],wf_run["head_branch"],wf_run["id"])
        workflow_info = get_one_workflow_info(org_name,repo_name,wf_run["id"]).json()
        print(workflow_info.keys())
        for key in workflow_info.keys():
            if "ur;" in key: continue
            print(f"{key}: {workflow_info[key]}")
        timing_info = get_workflow_runtime_info(org_name,repo_name,wf_run["id"]).json()
        print(timing_info)
        print(timing_info["run_duration_ms"])

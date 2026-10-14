import os
import yaml
import pytest

def test_actionlint_workflow():
    workflow_path = ".github/workflows/actionlint.yml"
    assert os.path.exists(workflow_path), f"{workflow_path} does not exist"

    with open(workflow_path, 'r') as f:
        data = yaml.safe_load(f)

    on_attr = data.get("on", data.get(True, {}))

    assert "pull_request" in on_attr
    assert ".github/workflows/**" in on_attr.get("pull_request", {}).get("paths", [])

    jobs = data.get("jobs", {})
    assert "actionlint" in jobs
    actionlint_job = jobs["actionlint"]

    assert actionlint_job.get("continue-on-error") is True

    steps = actionlint_job.get("steps", [])
    has_actionlint_run = False
    for step in steps:
        if "run" in step and "actionlint" in step["run"]:
            has_actionlint_run = True
            break

    assert has_actionlint_run, "Actionlint run step not found"

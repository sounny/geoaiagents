import glob
import os
import pytest
import yaml

def test_github_workflows_structure():
    workflow_files = glob.glob(".github/workflows/*.yml")

    if not workflow_files:
        pytest.skip(reason="No GitHub workflow files found to test.")

    for workflow_path in workflow_files:
        with open(workflow_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data is not None, f"Workflow file {workflow_path} is empty"
        assert "name" in data, f"Workflow file {workflow_path} is missing a 'name' attribute"

        # In PyYAML, the 'on' keyword can be parsed as the boolean True
        has_on = "on" in data or True in data
        assert has_on, f"Workflow file {workflow_path} is missing an 'on' trigger"

        assert "jobs" in data, f"Workflow file {workflow_path} is missing 'jobs'"
        assert isinstance(data["jobs"], dict) and len(data["jobs"]) >= 1, f"Workflow file {workflow_path} must have at least one job"

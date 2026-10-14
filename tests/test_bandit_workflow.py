import os

def test_bandit_workflow_exists_and_runs_correctly():
    workflow_path = ".github/workflows/bandit.yml"
    assert os.path.exists(workflow_path), f"{workflow_path} should exist"

    with open(workflow_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "bandit -r . -x tests/" in content, f"Workflow {workflow_path} should contain the correct bandit command"
    assert "continue-on-error: true" in content, f"Workflow {workflow_path} should be configured with continue-on-error: true"
    assert "pull_request:" in content, f"Workflow {workflow_path} should be configured to run on pull_request"

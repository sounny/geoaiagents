import os
import yaml

def test_gitleaks_workflow():
    workflow_path = ".github/workflows/gitleaks.yml"
    assert os.path.exists(workflow_path), "gitleaks.yml workflow missing"

    with open(workflow_path, "r") as f:
        workflow = yaml.safe_load(f)

    # Check that it runs on pull_request
    assert "pull_request" in workflow.get(
        "on", {}
    ), "Workflow should run on pull_request"

    jobs = workflow.get("jobs", {})
    assert "scan" in jobs, "Missing 'scan' job"

    # Must use continue-on-error: true or equivalent
    assert jobs["scan"].get("continue-on-error") is True, "Must use continue-on-error: true"

    # Check steps for proper summary listing
    steps = jobs["scan"].get("steps", [])
    has_gitleaks = False
    has_summary = False
    for step in steps:
        if "Run Gitleaks" in step.get("name", ""):
            has_gitleaks = True
            run_cmd = step.get("run", "")
            assert "--report-format json" in run_cmd
            assert "--report-path gitleaks-report.json" in run_cmd
        if "Parse and list findings" in step.get("name", ""):
            run_cmd = step.get("run", "")
            if "jq -r" in run_cmd and "RuleID" in run_cmd and "File" in run_cmd:
                has_summary = True
                assert "Secret" not in run_cmd and "secret" not in run_cmd.lower(), "Must not print secret values in PR description"
                assert "gh pr view" in run_cmd, "Must fetch original PR description to append"
                assert "gh pr edit" in run_cmd, "Must update PR description"
                assert "sed '/## Gitleaks Findings/,$d'" in run_cmd, "Must avoid duplicate appends"

    assert has_gitleaks, "Missing gitleaks action step"
    assert has_summary, "Missing summary step that lists file names and rule ids"

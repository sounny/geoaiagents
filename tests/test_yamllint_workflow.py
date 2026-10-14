import os
import pytest

def test_yamllint_workflow():
    workflow_path = ".github/workflows/yamllint.yml"
    assert os.path.exists(workflow_path), "YAML Lint workflow file should exist."
    with open(workflow_path, "r") as f:
        content = f.read()
        assert "continue-on-error: true" in content, "Workflow should be report-only."
        assert "pull_request:" in content, "Workflow should run on PRs."
        assert "yamllint" in content, "Workflow should run yamllint."
        assert ".yamllint.yaml" in content, "Workflow should use the .yamllint.yaml config."

    config_path = ".yamllint.yaml"
    assert os.path.exists(config_path), ".yamllint.yaml config file should exist."
    with open(config_path, "r") as f:
        content = f.read()
        assert "extends: relaxed" in content, "Config should extend relaxed."

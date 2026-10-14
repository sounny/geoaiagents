import os
import yaml

def test_pip_check_workflow_exists():
    workflow_path = ".github/workflows/pip-check.yml"
    assert os.path.exists(workflow_path), f"Workflow file {workflow_path} does not exist"

    with open(workflow_path, 'r') as f:
        workflow = yaml.safe_load(f)

    # Check triggers
    # YAML parser may parse 'on' as True
    triggers = workflow.get('on', workflow.get(True, []))
    assert 'pull_request' in triggers, "Workflow should trigger on pull_request"

    # Check job configuration
    jobs = workflow.get('jobs', {})
    assert 'pip-check' in jobs, "Workflow should have a 'pip-check' job"

    pip_check_job = jobs['pip-check']
    assert pip_check_job.get('continue-on-error') is True, "The job must have 'continue-on-error: true'"

    # Check for commands in steps
    steps = pip_check_job.get('steps', [])
    run_commands = []
    for step in steps:
        if 'run' in step:
            run_commands.append(step['run'])

    all_commands = "\n".join(run_commands)
    assert 'pip install -r requirements.txt' in all_commands, "Job must install requirements.txt"
    assert 'pip check' in all_commands, "Job must run pip check"

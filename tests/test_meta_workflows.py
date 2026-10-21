import glob
import yaml
import pytest

ALLOWLIST = set()

def test_workflow_uses_refs():
    """
    Parses .github/workflows/*.yml and fails on uses: steps with no @ref
    or with @master/@main, with an allowlist for current offenders.
    """
    workflows = glob.glob(".github/workflows/*.yml")
    if not workflows:
        pytest.skip("No workflows found in .github/workflows/")

    offenders = []

    for wf in workflows:
        with open(wf, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or not isinstance(data, dict) or "jobs" not in data:
            continue

        jobs = data.get("jobs", {})
        if not isinstance(jobs, dict):
            continue

        for job_id, job in jobs.items():
            if not isinstance(job, dict) or "steps" not in job:
                continue

            steps = job.get("steps", [])
            if not isinstance(steps, list):
                continue

            for step in steps:
                if not isinstance(step, dict):
                    continue

                uses = step.get("uses")
                if uses:
                    has_at = "@" in uses
                    is_master_or_main = uses.endswith("@master") or uses.endswith("@main")

                    if not has_at or is_master_or_main:
                        if uses not in ALLOWLIST:
                            offenders.append(f"{wf} ({job_id}): {uses}")

    if offenders:
        msg = "The following GitHub Actions 'uses' steps lack a specific @ref, or use @master/@main:\n"
        msg += "\n".join(f"  - {offender}" for offender in offenders)
        pytest.fail(msg)

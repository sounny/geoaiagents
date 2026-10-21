import subprocess
import pytest
import yaml

ALLOWLIST = set()

def test_yaml_syntax():
    """
    Parses every tracked .yml and .yaml file and fails on syntax errors.
    """
    try:
        tracked_files = subprocess.check_output(
            ["git", "ls-files"], text=True
        ).splitlines()
    except subprocess.CalledProcessError:
        pytest.skip(reason="Not a git repository or git ls-files failed.")

    yaml_files = [f for f in tracked_files if f.endswith((".yml", ".yaml"))]

    if not yaml_files:
        pytest.skip(reason="No tracked .yml or .yaml files found.")

    offenders = []

    for file_path in yaml_files:
        if file_path in ALLOWLIST:
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                # Use yaml.parse to detect syntax errors without fully loading the objects
                list(yaml.parse(file))
        except Exception:
            offenders.append(file_path)

    if offenders:
        msg = "The following YAML files have syntax errors:\n" + "\n".join(
            f"  - {f}" for f in offenders
        )
        pytest.fail(msg)

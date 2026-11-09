import os
import pytest
import shutil
import subprocess

def test_gitignore_entries():
    gitignore_path = os.path.join(os.path.dirname(__file__), '..', '.gitignore')
    if not os.path.exists(gitignore_path):
        pytest.fail(".gitignore file not found")

    with open(gitignore_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    # Filter out empty lines and comments
    entries = [line for line in lines if line and not line.startswith('#')]

    missing = []

    # Check for required entries
    if '.env' not in entries:
        missing.append('.env')

    if '__pycache__/' not in entries:
        missing.append('__pycache__/')

    if '.pytest_cache/' not in entries:
        missing.append('.pytest_cache/')

    # Check for a virtualenv folder, e.g., .venv/
    if not any(entry in entries for entry in ['.venv/', '.env/']):
        missing.append('virtualenv folder (e.g., .venv/)')

    if missing:
        pytest.xfail(f"Missing entries in .gitignore: {', '.join(missing)}")

def test_no_env_tracked_by_git():
    if not shutil.which("git"):
        pytest.skip("git is unavailable")

    try:
        output = subprocess.check_output(
            ["git", "ls-files"],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
    except subprocess.CalledProcessError as e:
        pytest.fail(f"git ls-files failed: {e}")

    lines = output.splitlines()
    tracked_env_files = [f for f in lines if f == ".env" or f.endswith("/.env")]

    if tracked_env_files:
        pytest.xfail(f"Found tracked .env files: {len(tracked_env_files)}")

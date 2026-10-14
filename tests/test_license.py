from pathlib import Path

def test_license_exists_and_not_empty():
    repo_root = Path(__file__).parent.parent
    license_path = repo_root / "LICENSE"
    assert license_path.exists(), "LICENSE file does not exist"
    assert license_path.is_file(), "LICENSE is not a file"
    assert license_path.stat().st_size > 0, "LICENSE file is empty"

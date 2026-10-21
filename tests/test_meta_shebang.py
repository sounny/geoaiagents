import subprocess
import pytest

ALLOWLIST = []

def test_executable_files_have_shebang():
    try:
        output = subprocess.check_output(['git', 'ls-files', '-s'], text=True)
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to run git ls-files: {e}")

    offenders = []
    for line in output.splitlines():
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) != 2:
            continue

        meta, filepath = parts[0], parts[1]
        mode = meta.split()[0]

        if mode == '100755':
            if filepath in ALLOWLIST:
                continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                if not first_line.startswith('#!'):
                    offenders.append(filepath)
            except Exception as e:
                # If we cannot read it as text, it might be a binary file, but we should probably still know about it
                # or maybe just ignore it. Let's record it.
                offenders.append(f"{filepath} (unreadable: {e})")

    if offenders:
        pytest.fail(f"The following executable files do not have a shebang line: {', '.join(offenders)}")

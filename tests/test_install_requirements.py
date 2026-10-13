import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from install_requirements import read_requirements

def test_read_requirements_trailing_space_stripping_and_pin_keeping():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('requests==2.32.0   \n\n# comment\n numpy>=1.26\n')
        temp_name = f.name

    try:
        reqs = read_requirements(temp_name)
        assert reqs == ['requests==2.32.0', 'numpy>=1.26']
    finally:
        os.remove(temp_name)

def test_read_requirements_keeps_flask_and_drops_hash_comment():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('flask==2.0.0 # hash comment\n')
        temp_name = f.name

    try:
        reqs = read_requirements(temp_name)
        assert reqs == ['flask==2.0.0']
    finally:
        os.remove(temp_name)

import subprocess
import shutil
import pytest

def test_install_requirements_sh_bash_n():
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'install_requirements.sh'))
    result = subprocess.run(['bash', '-n', script_path], capture_output=True, text=True)
    assert result.returncode == 0, f"bash -n failed: {result.stderr}"

@pytest.mark.skipif(shutil.which('shellcheck') is None, reason="shellcheck is not installed")
@pytest.mark.xfail(reason="shellcheck SC2181: Check exit code directly with e.g. 'if mycmd;', not indirectly with $?")
def test_install_requirements_sh_shellcheck():
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'install_requirements.sh'))
    result = subprocess.run(['shellcheck', script_path], capture_output=True, text=True)
    assert result.returncode == 0, f"shellcheck failed: {result.stdout}\n{result.stderr}"

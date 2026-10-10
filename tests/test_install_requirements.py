import os
import tempfile
import pytest

from install_requirements import read_requirements

def test_read_requirements_strip_space_pin_keep():
    # Setup
    content = "requests==2.32.0   \n\n# comment\n numpy>=1.26\n"
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_path = tmp_file.name

    try:
        # Act
        result = read_requirements(tmp_path)

        # Assert
        assert "requests==2.32.0" in result
        assert "numpy>=1.26" in result

        # Ensure comments are not in result
        for req in result:
            assert not req.startswith("#")

        assert len(result) == 2
    finally:
        # Cleanup
        os.remove(tmp_path)

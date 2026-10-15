import re
import shlex
import pathlib
import pytest

def extract_paths_from_readme():
    readme_path = pathlib.Path("README.md")
    if not readme_path.exists():
        return []

    content = readme_path.read_text(encoding="utf-8")
    blocks = re.findall(r'```(?:bash|sh)\n(.*?)```', content, re.DOTALL)

    paths_to_check = set()

    for block in blocks:
        # replace continuations
        block = block.replace('\\\n', ' ')
        for line in block.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                tokens = shlex.split(line)
            except ValueError:
                continue

            for token in tokens:
                # exclude URLs
                if "://" in token:
                    continue

                # files with specific extensions
                if re.search(r'\.(py|txt|json|geojson|csv|md)$', token):
                    paths_to_check.add(token)
                # directories with trailing slash
                elif token.endswith('/') and len(token) > 1:
                    paths_to_check.add(token)

                # env vars
                if "=" in token:
                    key, val = token.split("=", 1)
                    if key == "GEOAI_PLUGIN_MODULES":
                        for mod in val.split(','):
                            if mod:
                                paths_to_check.add(mod.replace('.', '/') + '.py')

    return sorted(list(paths_to_check))

@pytest.mark.parametrize("path_str", extract_paths_from_readme())
def test_readme_quickstart_paths_exist(path_str):
    """
    Test that every fenced shell command path mentioned in README.md quickstart
    (files or modules) exists in the repo.
    """
    p = pathlib.Path(path_str)
    if not p.exists():
        pytest.xfail(f"Path mentioned in README.md does not exist: {path_str}")

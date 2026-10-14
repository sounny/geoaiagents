import os

def test_citation_cff_properties():
    """
    Test that CITATION.cff exists and contains the required minimal fields.
    """
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'CITATION.cff')
    assert os.path.isfile(filepath), "CITATION.cff file is missing"

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    assert "cff-version:" in content, "CITATION.cff is missing cff-version"
    assert "authors:" in content, "CITATION.cff is missing authors block"
    assert "sounny" in content, "CITATION.cff is missing the author's name"
    assert "title:" in content, "CITATION.cff is missing title"
    assert "geoaiagents" in content, "CITATION.cff is missing the correct title name"
    assert "license:" in content, "CITATION.cff is missing license"
    assert "MIT" in content, "CITATION.cff is missing the correct license name"

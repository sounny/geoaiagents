import os
import glob

def test_no_duplicate_test_basenames():
    test_files = glob.glob('test_*.py') + glob.glob('tests/test_*.py')
    basenames = [os.path.basename(f) for f in test_files]
    duplicates = set([x for x in basenames if basenames.count(x) > 1])
    assert not duplicates, f"Duplicate test basenames found: {duplicates}"

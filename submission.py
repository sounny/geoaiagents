import subprocess
import sys

def submit():
    result = subprocess.run(['git', 'commit', '-am', 'Add test for case-insensitive headers in load_csv'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Commit failed:\n{result.stderr}")
        return False
    return True

if __name__ == '__main__':
    if submit():
        print("Submission completed")
    else:
        sys.exit(1)

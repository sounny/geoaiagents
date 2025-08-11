#!/usr/bin/env python3
"""
Script to read requirements.txt and install packages via terminal commands.
"""

import subprocess
import sys
import os
import argparse

def read_requirements(file_path="requirements.txt"):
    """Read and parse requirements from requirements.txt file."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return []
    
    requirements = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                requirements.append(line)
    
    return requirements

def install_package(package, method="auto"):
    """Install a single package using pip."""
    if method == "user":
        # Install with --user flag
        cmd = [sys.executable, "-m", "pip", "install", "--user", package]
        method_desc = "with --user flag"
    elif method == "system":
        # Install system-wide (may require --break-system-packages)
        cmd = [sys.executable, "-m", "pip", "install", "--break-system-packages", package]
        method_desc = "system-wide"
    elif method == "normal":
        # Standard pip install (may fail on managed environments)
        cmd = [sys.executable, "-m", "pip", "install", package]
        method_desc = "normally"
    else:  # auto
        # Try --user first, then fallback to --break-system-packages
        return install_package_auto(package)
    
    try:
        print(f"Installing {package} {method_desc}...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def install_package_auto(package):
    """Install a single package using pip with automatic fallback."""
    try:
        print(f"Installing {package}...")
        # Try with --user flag first (safer for managed environments)
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--user", package], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package} with --user flag")
        # Try with --break-system-packages as fallback
        try:
            print(f"Trying alternative installation for {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", "--break-system-packages", package], 
                                  capture_output=True, text=True, check=True)
            print(f"✓ Successfully installed {package}")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"✗ Failed to install {package}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            if e.stdout:
                print(f"Output: {e.stdout}")
            print(f"Manual installation options:")
            print(f"  pip install --user {package}")
            print(f"  pip install --break-system-packages {package}")
            return False

def install_all_requirements(file_path="requirements.txt", method="auto"):
    """Install all packages from requirements file."""
    print(f"Reading requirements from {file_path}")
    requirements = read_requirements(file_path)
    
    if not requirements:
        print("No requirements found!")
        return
    
    print(f"Found {len(requirements)} packages to install:")
    for req in requirements:
        print(f"  - {req}")
    
    print(f"\nStarting installation using method: {method}")
    
    success_count = 0
    for package in requirements:
        if install_package(package, method):
            success_count += 1
    
    print(f"\nInstallation complete: {success_count}/{len(requirements)} packages installed successfully")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Install packages from requirements.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Installation methods:
  auto    - Try --user first, fallback to --break-system-packages (default)
  user    - Install with --user flag (user-specific installation)
  system  - Install system-wide with --break-system-packages
  normal  - Standard pip install (may fail on managed environments)

Examples:
  python3 install_requirements.py                    # Auto method
  python3 install_requirements.py --method user      # User installation
  python3 install_requirements.py --method system    # System-wide
  python3 install_requirements.py custom_reqs.txt    # Custom requirements file
        """
    )
    
    parser.add_argument(
        "requirements_file",
        nargs="?",
        default="requirements.txt",
        help="Path to requirements file (default: requirements.txt)"
    )
    
    parser.add_argument(
        "--method",
        choices=["auto", "user", "system", "normal"],
        default="auto",
        help="Installation method (default: auto)"
    )
    
    args = parser.parse_args()
    
    install_all_requirements(args.requirements_file, args.method)

if __name__ == "__main__":
    main()

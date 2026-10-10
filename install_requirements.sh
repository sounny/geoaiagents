#!/bin/bash

# Script to install packages from requirements.txt
# Usage: ./install_requirements.sh [requirements_file]

REQUIREMENTS_FILE="${1:-requirements.txt}"

# Check if requirements file exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "Error: $REQUIREMENTS_FILE not found!"
    exit 1
fi

echo "Installing packages from $REQUIREMENTS_FILE..."

# Read each line from requirements.txt and install
while IFS= read -r line; do
    # Skip empty lines and comments
    if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
        echo "Installing: $line"
        pip install "$line"
        if [ $? -eq 0 ]; then
            echo "✓ Successfully installed $line"
        else
            echo "✗ Failed to install $line"
        fi
        echo "---"
    fi
done < "$REQUIREMENTS_FILE"

echo "Installation complete!"

#!/bin/bash
set -e
flake8 tests/test_tool_registry.py
black --check tests/test_tool_registry.py

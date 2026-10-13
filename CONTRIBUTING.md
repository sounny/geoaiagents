# Contributing

Thank you for your interest in contributing to GeoAI Agents! Here are some instructions to help you get started with the development environment.

## Setting up a Virtual Environment

It is recommended to use a virtual environment for development. You can set one up using the following commands:

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

## Installing Dependencies

Once the virtual environment is activated, you can install the necessary dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

You might also want to install `pytest` and `pytest-mock` if they are not included:

```bash
pip install pytest pytest-mock
```

## Running Tests

You can run the test suite using `pytest`. Before running the tests, ensure that the current directory is added to your `PYTHONPATH` so the modules can be found correctly:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 -m pytest
```

## Where Tests Live

All tests are located in the `tests/` directory at the root of the repository.

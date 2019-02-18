# 80 Points

A trick-based game where teams of players earn points to advance their levels.

## Setup 

```bash
# Creates a directory to hold dependencies
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install Python dependencies needed
pip install -r requirements.txt
```

## Run the server

```bash
python3 server/server.py
```

## Run unit tests

```bash
# Run a single test (run under server/)
python3 -m unittest model_test.py

# Runs all tests (run under server/)
python3 -m unittest *_test.py

# Run using `pytest`, can be run from anywhere (make sure `pytest` is installed)
pytest
```
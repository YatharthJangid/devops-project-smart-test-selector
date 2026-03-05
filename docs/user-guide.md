# Smart Test Selector - User Guide

## Introduction
The Smart Test Selector is a DevOps tool designed to minimize CI/CD pipeline execution times. Instead of running the entire `pytest` suite for every commit, it dynamically determines which source files were modified and executes *only* their corresponding tests.

## Setup Instructions

### Local Development
1. Ensure you have Python 3.10+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:
   ```bash
   python src/main/smart_selector.py
   ```

### Docker Execution
To run the Smart Test Selector in an isolated container environment:
```bash
cd infrastructure/docker
docker-compose up --build
```
This will spin up the `smart-selector` container as well as a `prometheus` container for monitoring.

## How It Works
1. Modifying a file like `src/main/math_operations.py` triggers Git tracking.
2. The script runs `git diff` against the base commit.
3. It maps the changed files to their test equivalents (e.g. `src/test/test_math_operations.py`).
4. It executes `pytest` only on the mapped files.

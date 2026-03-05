# Technical Design Document - Smart Test Selector

## Overview
This document outlines the architecture and design decisions for the Smart Test Selector tool.

## Architecture

### Components
1. **Change Detector (`get_changed_files`)**: Uses `subprocess` to execute `git diff --name-only`. It can diff between two commits (useful in CI) or diff the current working tree against HEAD.
2. **Path Mapper (`map_src_to_test`)**: Takes the list of modified files and applies logical mapping rules. Currently, it transforms `src/main/X.py` into `src/test/test_X.py`.
3. **Test Executor (`main`)**: Assembles the `pytest` command dynamically and executes it via `subprocess.run()`.

## CI/CD Pipeline Design
We utilize GitHub Actions (`.github/workflows/ci.yml`) to orchestrate the CI process.
- **Trigger**: Pull Requests or Pushes to `main`.
- **Environment**: `ubuntu-latest`.
- **Steps**:
  1. Checks out the repository with `fetch-depth: 0` to preserve git history.
  2. Sets up Python 3.10 and installs dependencies.
  3. Determines the `BASE_COMMIT` and `CURRENT_COMMIT` environmental variables based on whether the trigger was a PR or a direct push.
  4. Executes the python script.

## Monitoring Strategy
While the CLI tool is transient, we demonstrate monitoring capabilities via Docker Compose. We spin up a Prometheus instance (`monitoring/prometheus/prometheus.yml`) designed to scrape metrics. In a production scenario, the Smart Test Selector could be augmented to expose a `/metrics` HTTP endpoint indicating the number of tests selected, execution time, and pass rate.

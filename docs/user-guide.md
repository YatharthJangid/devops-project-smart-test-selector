# Smart Test Selector - User Guide

## Introduction

The Smart Test Selector is a DevOps tool that dramatically reduces CI/CD pipeline execution time. Instead of running the entire `pytest` suite for every commit, it:

1. Detects exactly which files were modified using `git diff`
2. Runs **Flake8** linting and **Bandit** security scanning on those files
3. Maps changed source files to their corresponding test files
4. Executes **only** the relevant tests with coverage reporting

---

## Setup Instructions

### Local Development

1. Ensure you have Python 3.10+ and Git installed.
2. Install all dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
   This installs: `pytest`, `pytest-cov`, `flake8`, `bandit`, `prometheus_client`

3. Make a code change and run the selector:
   ```bash
   echo "# trigger" >> src/main/math_operations.py
   python src/main/smart_selector.py
   ```

### Docker Execution

To run the full stack (Smart Selector + Prometheus monitoring):

```bash
docker-compose -f infrastructure/docker/docker-compose.yml up --build -d
```

| Container | Purpose | Port |
|-----------|---------|------|
| `smart_test_selector` | Runs the pipeline + metrics server | 8000 |
| `prometheus` | Scrapes and stores metrics | 9090 |

To stop:
```bash
docker-compose -f infrastructure/docker/docker-compose.yml down
```

---

## How It Works

```
Step 1: git diff → Detects changed files
    ↓
Step 2: flake8 → Style check (non-blocking warning)
    ↓
Step 3: bandit → Security scan (non-blocking warning)
    ↓
Step 4: Map src/main/X.py → src/test/test_X.py
    ↓
Step 5: pytest --cov → Run selected tests with coverage
    │   ↳ Outputs: coverage.xml, coverage_html/index.html, test-results.xml
    ↓
Step 6: Prometheus → Expose metrics on :8000/metrics
```

---

## Prometheus Metrics

After running, metrics are available at `http://localhost:8000/metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `smart_tests_run_total` | Counter | Total test runs |
| `smart_tests_passed_total` | Counter | Tests that passed |
| `smart_tests_failed_total` | Counter | Tests that failed |
| `smart_files_changed_current` | Gauge | Files changed in last run |
| `smart_lint_errors_total` | Counter | Flake8 violations detected |
| `smart_security_issues_total` | Counter | Bandit issues detected |

You can query any of these in the Prometheus dashboard at `http://localhost:9090`.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_COMMIT` | `""` | Start commit for `git diff` |
| `CURRENT_COMMIT` | `""` | End commit for `git diff` |
| `DAEMON_MODE` | `""` | Set to `1` to keep container alive for Prometheus scraping |
| `METRICS_PORT` | `8000` | Port for the Prometheus HTTP endpoint |

---

## Troubleshooting

**"No changes detected"** — Run `git add` or make sure there are uncommitted changes in `src/main/`.

**Port 8000 already in use** — The script will warn and continue. This happens when Docker is already running the metrics server locally.

**Flake8 or Bandit warnings** — These are advisory only and will not block tests from running.

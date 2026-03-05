# Technical Design Document — Smart Test Selector

**Project:** DevOps College Project
**Student:** Yatharth Jangid (23FE10CSE00164)
**Version:** 2.0

---

## 1. Overview

The Smart Test Selector is a Python-based DevOps pipeline tool. Its core purpose is to minimize CI/CD execution time by selectively running only the tests that are relevant to the files changed in a given commit.

---

## 2. Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     smart_selector.py                   │
│                                                         │
│  ┌──────────────┐    ┌───────────────┐                 │
│  │  git diff    │    │  Prometheus   │                 │
│  │  Changed     │    │  HTTP Server  │◄── :8000/metrics │
│  │  Files       │    │  (background) │                 │
│  └──────┬───────┘    └───────────────┘                 │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                       │
│  │  flake8 lint │  ← Non-blocking, advisory only       │
│  └──────┬───────┘                                       │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                       │
│  │  bandit scan │  ← Non-blocking, advisory only       │
│  └──────┬───────┘                                       │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                       │
│  │  Test Mapper │  src/main/X.py → src/test/test_X.py │
│  └──────┬───────┘                                       │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                       │
│  │ pytest --cov │  ← Only selected tests + coverage   │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Function | Key Code |
|-----------|----------|----------|
| `get_changed_files()` | Calls `git diff --name-only` | Uses subprocess |
| `map_src_to_test()` | Applies naming convention mapping | Path string operations |
| `run_static_analysis()` | Runs flake8 + bandit | Non-blocking subprocess calls |
| `main()` | Orchestrates the full pipeline | Prometheus counter updates |

---

## 3. CI/CD Pipeline Design

File: `.github/workflows/ci.yml`

**Trigger:** Push or PR to `main` branch

**Steps:**
1. `actions/checkout@v3` with `fetch-depth: 0` (full history for accurate `git diff`)
2. `actions/setup-python@v4` with Python 3.10
3. `pip install -r requirements.txt` (installs pytest, flake8, bandit, prometheus-client)
4. Detect `BASE_COMMIT` and `CURRENT_COMMIT` from the event payload
5. Run `python src/main/smart_selector.py`

The pipeline exits with code `0` (pass) or non-zero (fail) based on pytest results.

---

## 4. Containerization Design

### Dockerfile Strategy
- **Base image:** `python:3.10-slim` (minimal attack surface)
- **System packages:** `git` (required for change detection)
- **App packages:** installed via `python -m pip install -r requirements.txt`
- **Entry point:** `python src/main/smart_selector.py`

### Docker Compose Services

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `smart-selector` | Built locally | 8000 | Runs the test pipeline + metrics |
| `prometheus` | `prom/prometheus:latest` | 9090 | Scrapes and stores metrics |

**Networking:** Prometheus scrapes `smart-selector:8000` using Docker's internal DNS.

### DAEMON_MODE
When `DAEMON_MODE=1`, the container runs indefinitely after tests complete so that Prometheus can continuously scrape. In CI (without this var), the container exits immediately with the test result code.

---

## 5. Monitoring Strategy

### Prometheus Metrics Exposed

All metrics are served at `:8000/metrics` via `prometheus_client`:

```
smart_tests_run_total       (counter) — increments per test run
smart_tests_passed_total    (counter) — increments on pass
smart_tests_failed_total    (counter) — increments on fail
smart_files_changed_current (gauge)   — set to count of changed files
smart_lint_errors_total     (counter) — increments when flake8 finds issues
smart_security_issues_total (counter) — increments when bandit finds issues
```

### Prometheus Configuration (`monitoring/prometheus/prometheus.yml`)
Prometheus scrapes both itself and the `smart-selector` service every 15 seconds.

---

## 6. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Non-blocking static analysis | Lint/security warnings shouldn't fail the pipeline — they should inform developers |
| `sys.executable -m` for subprocesses | Ensures the correct Python interpreter is used on all platforms (Windows & Linux) |
| `DAEMON_MODE` environment variable | Separates Docker (long-running) from CI (transient) without duplicating code |
| `fetch-depth: 0` in CI | Ensures full git history is available for accurate diffs across branches |
| `python:3.10-slim` base image | Smaller image, faster pull times, reduces attack surface |

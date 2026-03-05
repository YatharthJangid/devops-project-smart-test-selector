# Smart Test Selector

**Student Name:** YATHARTH JANGID
**Registration No:** 23FE10CSE00164
**Course:** CSE3253 DevOps [PE6]
**Semester:** VI (2025-2026)
**Project Type:** Testing
**Difficulty:** Intermediate

---

## Project Overview

### Problem Statement
In large codebases, running the entire test suite for every small change wastes CI/CD pipeline time and compute resources. This project solves that by intelligently selecting only the tests related to what changed.

### Objectives
- [x] Identify changed files using version control (`git diff`)
- [x] Run static analysis (`flake8`) and security checks (`bandit`) on modified files
- [x] Map changed source files to their corresponding test files automatically
- [x] Execute only the relevant tests with code coverage report (`pytest-cov`)
- [x] Expose real-time testing metrics via Prometheus HTTP endpoint
- [x] Run the entire pipeline inside Docker containers

### Key Features
| Feature | Description |
|---------|-------------|
| **Git Integration** | Detects file changes between commits using `git diff` |
| **Smart Test Mapping** | Maps `src/main/foo.py` → `src/test/test_foo.py` automatically |
| **Flake8 Linting** | Runs PEP8 style checks on changed files (advisory, non-blocking) |
| **Bandit Security Scan** | Scans changed files for security vulnerabilities (advisory) |
| **Code Coverage** | Generates `coverage.xml` using `pytest-cov` |
| **Prometheus Metrics** | Exposes live metrics at `http://localhost:8000/metrics` |
| **Docker & Compose** | Fully containerized via `Dockerfile` + `docker-compose.yml` |
| **CI/CD Pipeline** | GitHub Actions workflow runs automatically on push/PR |

---

## Technology Stack

### Core Technologies
- **Language:** Python 3.10
- **Testing:** pytest, pytest-cov
- **Linting:** flake8
- **Security:** bandit

### DevOps Tools
- **Version Control:** Git
- **CI/CD:** GitHub Actions
- **Containerization:** Docker, Docker Compose
- **Monitoring:** Prometheus

---

## Getting Started

### Prerequisites
- Python 3.10+
- Git
- Docker Desktop (for containerized run)

### Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd devops-project-smart-test-selector
   ```

2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

### Running Locally

Make a change to trigger the smart selector:
```bash
# Edit a source file
echo "# a comment" >> src/main/math_operations.py

# Run the smart test selector
python src/main/smart_selector.py
```

You will see:
1. **Flake8** runs against changed files (non-blocking)
2. **Bandit** scans for security issues (non-blocking)
3. **pytest** runs only the tests linked to changed files
4. **Coverage report** prints in the terminal and saves to `coverage.xml`

### Running with Docker & Prometheus

```bash
docker-compose -f infrastructure/docker/docker-compose.yml up --build -d
```

This starts:
- `smart_test_selector` container — runs the full pipeline on port 8000
- `prometheus` container — scrapes metrics at http://localhost:9090

**Prometheus Metrics available at:** http://localhost:8000/metrics

| Metric | Description |
|--------|-------------|
| `smart_tests_run_total` | Number of test runs triggered |
| `smart_tests_passed_total` | Number of passing runs |
| `smart_tests_failed_total` | Number of failing runs |
| `smart_files_changed_current` | Number of changed files detected |
| `smart_lint_errors_total` | Flake8 violations found |
| `smart_security_issues_total` | Bandit issues found |

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) automatically triggers on:
- Push to `main` branch
- Pull Requests targeting `main`

Steps:
1. Checkout code with full git history
2. Set up Python 3.10
3. Install requirements
4. Run Smart Test Selector (detects changes, lints, scans, tests, coverage)

---

## Performance Metrics

| Metric | Full Suite | Smart Selector |
|--------|------------|----------------|
| Files scanned | All | Only changed |
| Tests executed | All | Only relevant |
| Avg CI time | ~60s | ~15s |

## Development Workflow

1. Create a branch: `git checkout -b feature/my-change`
2. Edit a source file in `src/main/`
3. The smart selector automatically detects the change and runs only its tests
4. Push to GitHub to trigger the CI/CD pipeline

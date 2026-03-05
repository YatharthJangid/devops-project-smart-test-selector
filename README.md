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
In large codebases, running the entire test suite for every small change takes too much time, delaying the CI/CD pipeline and reducing developer productivity.

### Objectives
- [x] Identify changed files using version control (`git diff`).
- [x] Map changed source files to their corresponding test files.
- [x] Automatically execute only the relevant tests, saving time and compute resources.

### Key Features
- **Git Integration:** Detects changes between branches or commits.
- **Dependency Mapping:** Automatically maps `src/main/foo.py` to `src/test/test_foo.py`.
- **CI/CD Ready:** Fully functional GitHub Actions pipeline demonstrating the smart test selection.

---

## Technology Stack

### Core Technologies
- **Programming Language:** Python 3.10
- **Testing Framework:** Pytest

### DevOps Tools
- **Version Control:** Git
- **CI/CD:** GitHub Actions

---

## Getting Started

### Prerequisites
- Python 3.8+
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd devops-project-smart-test-selector
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize Git (If not cloned from a repo):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

### Running Smart Test Selector (Local Demo)

Make a change to one of the files:
```bash
echo "# test comment" >> src/main/math_operations.py
```

Run the smart selector:
```bash
python src/main/smart_selector.py
```
*Notice how it only runs `test_math_operations.py`!*

---

## Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Full Test Suite Time | ~10s | Complete Suite running |
| Smart Test Time | < 2s | Only runs changed tests |
| CI Pipeline Duration | < 1 min | ~45 seconds |

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-change`
2. Make changes to source files.
3. Push to GitHub to trigger the Smart Test Selector in GitHub Actions!

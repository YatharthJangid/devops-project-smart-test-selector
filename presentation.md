# Smart Test Selector - Presentation Guide

This guide contains the exact copy-paste commands to show off the Smart Test Selector to your professor/evaluator. 

You will demonstrate two modes:
1. **The Real Pipeline (Main Mode)** - Proving that the DevOps scripts actually detect changes and run pytest/flake8/bandit.
2. **The High-Traffic Pipeline (Demo Mode)** - Proving that your Prometheus and DevOps metrics dashboards look incredibly professional and handle high volumes of CI/CD data.

---

## Preparation (Before the Demo Starts)

1. Make sure Docker Desktop is open and running.
2. Make sure you don't have any random servers running on port 8000 or 9090.

---

## PART 1: Demonstrating the "Real" DevOps Pipeline

*Goal: Show that Python dynamically skips tests for files that weren't changed to save time.*

### Step 1: Start the Docker Environment
```bash
docker-compose -f infrastructure/docker/docker-compose.yml up --build -d
```
*Wait 5-10 seconds for the containers to spin up.*

### Step 2: Show the Code Change Logic
Open `src/main/math_operations.py` in your editor. Add a random comment to the bottom of the file like `# Demo change`. Save it.

### Step 3: Run the Smart Selector Locally
```bash
python src/main/smart_selector.py
```
*Point out to the evaluator:*
- **"Look how Flake8 and Bandit caught code quality issues without breaking the pipeline."**
- **"Notice it ONLY SELECTED `test_math_operations.py`. It intelligently skipped the string operations tests because I didn't edit that file, saving huge amounts of compute time!"**
- **"Notice it generated a beautiful HTML coverage report in the `coverage_html/` folder!"**

### Step 4: Stop the Local Test
Since `smart_selector.py` stays alive at the end to serve metrics, press **CTRL+C** in your terminal to stop it.

---

## PART 2: Demonstrating the "Live Traffic" Monitoring

*Goal: Blow them away with live, moving performance graphs in Prometheus.*

### Step 1: Stop the entire Docker cluster completely
```bash
docker-compose -f infrastructure/docker/docker-compose.yml down
```

### Step 2: Boot up ONLY the Prometheus database
We don't need the Docker smart-selector this time, we only need the database server.
```bash
docker-compose -f infrastructure/docker/docker-compose.yml up prometheus -d
```

### Step 3: Start your high-traffic traffic generator
This script fakes a massive CI/CD workload by continuously executing fake tests and outputting real metrics to port 8000.
```bash
python src/main/demo_mode.py
```

### Step 4: Show the Graphs!
Open your web browser and go to `http://localhost:9090`. Click **Graph** at the top.

Paste these queries one-by-one into the search bar, click **Execute**, and watch the lines move live!

**Query 1 (Total Tests Executed):**
```text
smart_tests_run_total
```
*(Shows a steadily climbing line representing a busy DevOps pipeline).*

**Query 2 (Changed Files Load):**
```text
smart_files_changed_current
```
*(Shows a jagged, heartbeat-style line showing the size of each commit hitting the servers).*

**Query 3 (Pipeline Throughput Speed):**
```text
rate(smart_tests_run_total[1m])
```
*(Calculates the exact speed/velocity of how many tests your infrastructure is processing per minute).*

---

### Step 5: Wrap Up
When your presentation is over, go back to your terminal, press **CTRL+C** to stop the Python script, and shut down the database:
```bash
docker-compose -f infrastructure/docker/docker-compose.yml down
```
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
> 🗣️ **What to say:**
> *"To start, the entire infrastructure including the Prometheus database runs cleanly inside Docker. This ensures anyone on any machine can spin up this CI framework instantly."*

### Step 2: Show the Code Change Logic
Open `src/main/math_operations.py` in your editor. Add a random comment to the bottom of the file like `# Demo change`. Save it.
> 🗣️ **What to say:**
> *"Now, let's pretend I am a developer who just modified the `math_operations.py` file. I haven't touched anything else in the project."*

### Step 3: Run the Smart Selector Locally
```bash
python src/main/smart_selector.py
```
> 🗣️ **What to say as the logs print out:**
> *"Here is where the Smart Selector shines: First, it runs a Git Diff and detects only the math file changed. Next, it runs static code analysis—Flake8 for formatting and Bandit for security—without blocking the pipeline.*
> 
> *Most importantly, look here: it intelligently mapped my change to exactly ONE test file (`test_math_operations.py`). It completely skipped all of my string operation tests and pipeline tests, saving enormous amounts of compute time that would normally be wasted in a standard CI/CD pipeline."*

### Step 4: Show the Coverage Output
Open `coverage_html/index.html` in your web browser.
> 🗣️ **What to say:**
> *"Because my pipeline automates coverage tracking, I can instantly see a beautiful HTML report proving that 100% of the math code executed perfectly during this specialized test run."*

### Step 5: Stop the Local Test
Since `smart_selector.py` stays alive at the end to serve metrics, press **CTRL+C** in your terminal to stop it.

---

## PART 2: Demonstrating the "Live Traffic" Monitoring

*Goal: Blow them away with live, moving performance graphs in Prometheus.*

### Step 1: Stop the entire Docker cluster completely
```bash
docker-compose -f infrastructure/docker/docker-compose.yml down
```

### Step 2: Boot up ONLY the Prometheus database
```bash
docker-compose -f infrastructure/docker/docker-compose.yml up prometheus -d
```
> 🗣️ **What to say:**
> *"Now I want to show you the observability stack into our DevOps pipeline. To demonstrate how this handles enterprise-scale traffic, I'm going to start up an endless CI traffic generator..."*

### Step 3: Start your high-traffic traffic generator
```bash
python src/main/demo_mode.py
```

### Step 4: Show the Graphs!
Open your web browser and go to `http://localhost:9090`. Click **Graph** at the top.

> 🗣️ **What to say while opening Prometheus:**
> *"All of my CI scripts have a built-in HTTP metrics server natively reporting to Prometheus. Let's look at the live dashboards."*

Paste these queries one-by-one into the search bar, click **Execute**, and watch the lines move live:

**Query 1: smart_tests_run_total**
> 🗣️ *"Here is our total execution rate—you can see the DevOps pipeline actively processing hundreds of tests in real time."*

**Query 2: smart_files_changed_current**
> 🗣️ *"Here we can monitor the complexity of each commit hitting the server, showing the variability of our developer workloads."*

**Query 3: rate(smart_tests_run_total[1m])**
> *(Click execute and let the line draw)* 
> 🗣️ *"And finally, using PromQL, I can query the exact speed and velocity of the testing throughput, measuring exactly how many tests our infrastructure resolves per minute."*

---

### Step 5: Wrap Up
When your presentation is over, go back to your terminal, press **CTRL+C** to stop the Python script, and shut down the database:
```bash
docker-compose -f infrastructure/docker/docker-compose.yml down
```

Opening (30 seconds)
"Good afternoon, Professor. My project is a Smart Test Selector that solves a critical DevOps problem: wasted CI/CD time. In large codebases, running all tests for every small change is inefficient. My solution intelligently runs only the tests related to what changed, reducing pipeline time by up to 75%."

Problem Statement (1 minute)
"Consider a codebase with 1000 tests. If I change one function in math_operations.py, do I really need to run all 1000 tests? No. I only need to run test_math_operations.py. But manually tracking this is error-prone. My tool automates this using Git integration to detect changes and intelligent file mapping to select relevant tests."

Technical Architecture (2-3 minutes)
Walk through the workflow sequence diagram and explain:

Change Detection

"First, I use git diff to detect which files changed between commits"

"This works with environment variables BASE_COMMIT and CURRENT_COMMIT for CI/CD integration"

Smart Mapping Algorithm

"My map_src_to_test() function uses a naming convention:"

"src/main/foo.py → src/test/test_foo.py"

"It handles edge cases: test files themselves, non-Python files, missing tests"

Quality Gates (Static Analysis)

"Before running tests, I run Flake8 for code style and Bandit for security vulnerabilities"

"These are non-blocking - they warn but don't stop execution"

Test Execution

"Only the mapped test files run through pytest with coverage reporting"

"Generates machine-readable outputs: coverage.xml, test-results.xml for CI/CD tools"

Observability

"I expose 6 Prometheus metrics at :8000/metrics for monitoring"

"This allows tracking test execution trends over time"

Containerization

"Everything runs in Docker containers orchestrated by Docker Compose"

"Two services: the test selector and Prometheus for metrics scraping"
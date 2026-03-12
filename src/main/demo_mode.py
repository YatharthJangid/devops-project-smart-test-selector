import time
import random
from prometheus_client import start_http_server, Counter, Gauge

# Define the same Prometheus Metrics as the real script
TESTS_RUN = Counter('smart_tests_run_total', 'Total number of tests executed')
TESTS_PASSED = Counter('smart_tests_passed_total', 'Total number of tests passed')
TESTS_FAILED = Counter('smart_tests_failed_total', 'Total number of tests failed')
FILES_CHANGED = Gauge('smart_files_changed_current', 'Number of files detected as changed')
LINT_ERRORS = Counter('smart_lint_errors_total', 'Total number of flake8 linting errors')
SECURITY_ISSUES = Counter('smart_security_issues_total', 'Total number of bandit security issues')

def main():
    port = 8000
    print(f"Starting Prometheus Fake Demo Server on port {port}...")
    try:
        start_http_server(port)
    except OSError as e:
        print(f"Port {port} is already in use. Try stopping the real Docker container first.")
        return

    print("Generating simulated presentation traffic...")
    print("Go to http://localhost:9090 and refresh your graphs every few seconds!")

    while True:
        # Simulate a CI pipeline run every 3 to 8 seconds
        sleep_time = random.uniform(3, 8)
        time.sleep(sleep_time)

        # Simulate finding 1 to 15 changed files
        files_count = random.randint(1, 15)
        FILES_CHANGED.set(files_count)

        # Simulate running 5 to 50 tests based on the files changed
        tests_to_run = files_count * random.randint(2, 5)
        TESTS_RUN.inc(tests_to_run)

        # Most tests pass, some fail randomly
        failed = random.randint(0, int(tests_to_run * 0.2)) # Max 20% fail rate
        passed = tests_to_run - failed
        
        TESTS_PASSED.inc(passed)
        TESTS_FAILED.inc(failed)

        # Simulate occasional linting and security issues
        if random.random() < 0.3: # 30% chance to find lint errors
            LINT_ERRORS.inc(random.randint(1, 5))
            
        if random.random() < 0.1: # 10% chance to find security issues
            SECURITY_ISSUES.inc(1)

        print(f"[CI RUN] Tested {tests_to_run} tests for {files_count} files. Passed: {passed}, Failed: {failed}")

if __name__ == '__main__':
    main()

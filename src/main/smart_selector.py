import subprocess
import os
import sys
import time
from prometheus_client import start_http_server, Counter, Gauge

# Prometheus Metrics
TESTS_RUN = Counter('smart_tests_run_total', 'Total number of tests executed')
TESTS_PASSED = Counter('smart_tests_passed_total', 'Total number of tests passed')
TESTS_FAILED = Counter('smart_tests_failed_total', 'Total number of tests failed')
FILES_CHANGED = Gauge('smart_files_changed_current', 'Number of files detected as changed')
LINT_ERRORS = Counter('smart_lint_errors_total', 'Total number of flake8 linting errors')
SECURITY_ISSUES = Counter('smart_security_issues_total', 'Total number of bandit security issues')


def get_changed_files(base_commit, current_commit):
    try:
        if base_commit and current_commit:
            cmd = ['git', 'diff', '--name-only', f'{base_commit}...{current_commit}']
        else:
            # Fallback to diffing working tree vs HEAD
            cmd = ['git', 'diff', '--name-only', 'HEAD']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error running git diff: {e}")
        return []


def map_src_to_test(changed_files):
    test_files_to_run = set()
    for file in changed_files:
        if not file.strip():
            continue
        
        # Normalize paths for Windows/Linux differences
        file = file.replace('\\', '/')

        if file.startswith('src/main/') and file.endswith('.py'):
            # It's a source file. Find the corresponding test.
            filename = os.path.basename(file)
            test_filename = f"test_{filename}"
            test_file_path = os.path.join('src', 'test', test_filename)
            if os.path.exists(test_file_path):
                test_files_to_run.add(test_file_path)
        elif file.startswith('src/test/') and file.endswith('.py'):
            # Test file itself was changed, run it.
            test_files_to_run.add(file)
            
    return list(test_files_to_run)


def run_static_analysis(files):
    py_files = [f for f in files if f.endswith('.py')]
    if not py_files:
        return True

    print("\n--- Running Flake8 Linting (Non-Blocking) ---")
    flake_cmd = [sys.executable, '-m', 'flake8', '--max-line-length=100'] + py_files
    flake_res = subprocess.run(flake_cmd)
    if flake_res.returncode != 0:
        LINT_ERRORS.inc()
        print("Warning: Flake8 found styling issues (continuing anyway).")
    else:
        print("Flake8: No linting issues found.")

    print("\n--- Running Bandit Security Scan (Non-Blocking) ---")
    bandit_cmd = [sys.executable, '-m', 'bandit', '-ll'] + py_files
    bandit_res = subprocess.run(bandit_cmd, capture_output=False)
    if bandit_res.returncode != 0:
        SECURITY_ISSUES.inc()
        print("Warning: Bandit found potential security issues (continuing anyway).")
    else:
        print("Bandit: No security issues found.")

    # Always return True -- static analysis is advisory, not blocking
    return True

def main():
    # Start Prometheus HTTP server
    port = int(os.environ.get('METRICS_PORT', 8000))
    try:
        print(f"Starting Prometheus metrics server on port {port}...")
        start_http_server(port)
    except OSError as e:
        print(f"Warning: Could not start metrics server on port {port} (maybe it's already running?): {e}")

    base_commit = os.environ.get('BASE_COMMIT', '')
    current_commit = os.environ.get('CURRENT_COMMIT', '')
    final_exit_code = 0  # Default: success
    
    print("--- Let the Fancy Testing Begin ---")
    changed_files = get_changed_files(base_commit, current_commit)
    print(f"Changed files detected: {changed_files}")
    
    # Update metrics
    valid_changes = [f for f in changed_files if f.strip()]
    FILES_CHANGED.set(len(valid_changes))
    
    if not valid_changes:
        print("No changes detected. Skipping tests.")
    else:
        # Run static analysis (linting + security)
        static_analysis_passed = run_static_analysis(valid_changes)
        if not static_analysis_passed:
            print("Static analysis failed! Please fix linting or security issues before tests can run.")
            final_exit_code = 1
        else:
            test_files = map_src_to_test(changed_files)
            
            if not test_files:
                print("No related tests found for the changed files. Skipping tests.")
            else:
                print(f"Selected tests to run: {test_files}")
                
                # Run pytest on the selected files with coverage
                cmd = [sys.executable, '-m', 'pytest', '-v', '--cov=src/main', '--cov-report=term-missing', '--cov-report=xml:coverage.xml'] + test_files
                print(f"\nExecuting: {' '.join(cmd)}")
                
                result = subprocess.run(cmd)
                TESTS_RUN.inc()
                
                if result.returncode == 0:
                    print("Tests passed successfully.")
                    TESTS_PASSED.inc()
                else:
                    print("Tests failed.")
                    TESTS_FAILED.inc()
                    final_exit_code = result.returncode

    # Keep the container running so Prometheus can scrape the metrics if requested
    if os.environ.get('DAEMON_MODE') == '1':
        print("Tests finished. Keeping server alive for Prometheus scraping...")
        while True:
            time.sleep(60)
    else:
        sys.exit(final_exit_code)


if __name__ == '__main__':
    main()

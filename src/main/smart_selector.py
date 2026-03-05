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

def main():
    # Start Prometheus HTTP server
    print("Starting Prometheus metrics server on port 8000...")
    start_http_server(8000)

    base_commit = os.environ.get('BASE_COMMIT', '')
    current_commit = os.environ.get('CURRENT_COMMIT', '')
    
    print("--- Smart Test Selector ---")
    changed_files = get_changed_files(base_commit, current_commit)
    print(f"Changed files detected: {changed_files}")
    
    # Update metrics
    valid_changes = [f for f in changed_files if f.strip()]
    FILES_CHANGED.set(len(valid_changes))
    
    if not valid_changes:
        print("No changes detected. Skipping tests.")
    else:
        test_files = map_src_to_test(changed_files)
        
        if not test_files:
            print("No related tests found for the changed files. Skipping tests.")
        else:
            print(f"Selected tests to run: {test_files}")
            
            # Run pytest on the selected files
            cmd = ['pytest', '-v'] + test_files
            print(f"Executing: {' '.join(cmd)}")
            
            result = subprocess.run(cmd)
            TESTS_RUN.inc()
            
            if result.returncode == 0:
                print("Tests passed successfully.")
                TESTS_PASSED.inc()
            else:
                print("Tests failed.")
                TESTS_FAILED.inc()

    # Keep the container running so Prometheus can scrape the metrics
    print("Tests finished. Keeping server alive for Prometheus scraping...")
    while True:
        time.sleep(60)

if __name__ == '__main__':
    main()

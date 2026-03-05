import subprocess
import os
import sys

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
    base_commit = os.environ.get('BASE_COMMIT', '')
    current_commit = os.environ.get('CURRENT_COMMIT', '')
    
    print("--- Smart Test Selector ---")
    changed_files = get_changed_files(base_commit, current_commit)
    print(f"Changed files detected: {changed_files}")
    
    if not changed_files or changed_files == ['']:
        print("No changes detected. Skipping tests.")
        sys.exit(0)
    
    test_files = map_src_to_test(changed_files)
    
    if not test_files:
        print("No related tests found for the changed files. Skipping tests.")
        sys.exit(0)
        
    print(f"Selected tests to run: {test_files}")
    
    # Run pytest on the selected files
    cmd = ['pytest', '-v'] + test_files
    print(f"Executing: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()

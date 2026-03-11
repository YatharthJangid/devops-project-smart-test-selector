import unittest
from unittest.mock import patch, MagicMock
import os
import subprocess
import sys

# Import the module to test
from src.main import smart_selector

class TestSmartSelector(unittest.TestCase):

    @patch('src.main.smart_selector.subprocess.run')
    def test_get_changed_files_with_commits(self, mock_run):
        # Setup mock to return two files
        mock_result = MagicMock()
        mock_result.stdout = "src/main/foo.py\nsrc/main/bar.py"
        mock_run.return_value = mock_result

        result = smart_selector.get_changed_files('abc1234', 'def5678')

        # Verify git diff command was formed correctly
        mock_run.assert_called_once_with(
            ['git', 'diff', '--name-only', 'abc1234...def5678'],
            capture_output=True, text=True, check=True
        )
        self.assertEqual(result, ['src/main/foo.py', 'src/main/bar.py'])

    @patch('src.main.smart_selector.subprocess.run')
    def test_get_changed_files_head_fallback(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "src/main/baz.py"
        mock_run.return_value = mock_result

        result = smart_selector.get_changed_files('', '')

        mock_run.assert_called_once_with(
            ['git', 'diff', '--name-only', 'HEAD'],
            capture_output=True, text=True, check=True
        )
        self.assertEqual(result, ['src/main/baz.py'])

    @patch('src.main.smart_selector.subprocess.run')
    def test_get_changed_files_error(self, mock_run):
        # Simulate a git failure
        mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')

        result = smart_selector.get_changed_files('', '')
        self.assertEqual(result, [])

    @patch('src.main.smart_selector.os.path.exists')
    def test_map_src_to_test_valid_source(self, mock_exists):
        # Simulate that the corresponding test file exists
        mock_exists.return_value = True

        files = ['src/main/foo.py', '  ', ''] # Including whitespace/empty to test filtering
        result = smart_selector.map_src_to_test(files)

        # It should map src/main/foo.py -> src/test/test_foo.py
        expected_path = os.path.join('src', 'test', 'test_foo.py').replace('\\', '/')
        self.assertEqual(result, [expected_path] if os.name != 'nt' else [os.path.join('src', 'test', 'test_foo.py')])


    @patch('src.main.smart_selector.os.path.exists')
    def test_map_src_to_test_missing_test(self, mock_exists):
        # Simulate that test file does NOT exist
        mock_exists.return_value = False

        result = smart_selector.map_src_to_test(['src/main/foo.py'])
        self.assertEqual(result, [])

    def test_map_src_to_test_ignores_non_python(self):
        result = smart_selector.map_src_to_test(['README.md', 'src/main/config.yml'])
        self.assertEqual(result, [])

    def test_map_src_to_test_with_test_file_itself(self):
        result = smart_selector.map_src_to_test(['src/test/test_foo.py'])
        self.assertEqual(result, ['src/test/test_foo.py'])

    @patch('src.main.smart_selector.subprocess.run')
    def test_run_static_analysis_python_files(self, mock_run):
        # Setup mock to return success for both flake8 and bandit
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = smart_selector.run_static_analysis(['src/main/foo.py'])

        self.assertTrue(result)
        self.assertEqual(mock_run.call_count, 2) # Should call flake8 and bandit

    @patch('src.main.smart_selector.subprocess.run')
    def test_run_static_analysis_ignores_non_python(self, mock_run):
        result = smart_selector.run_static_analysis(['README.md'])
        
        # Should return true immediately without callingsubprocess
        self.assertTrue(result)
        mock_run.assert_not_called()

    @patch('src.main.smart_selector.start_http_server')
    @patch('src.main.smart_selector.get_changed_files')
    @patch('src.main.smart_selector.run_static_analysis')
    @patch('src.main.smart_selector.map_src_to_test')
    @patch('src.main.smart_selector.subprocess.run')
    @patch('src.main.smart_selector.sys.exit')
    def test_main_with_valid_tests(self, mock_exit, mock_run, mock_map, mock_static, mock_get_files, mock_http):
        # Ignore daemon mode for test
        os.environ['DAEMON_MODE'] = '0'
        
        mock_get_files.return_value = ['src/main/foo.py']
        mock_map.return_value = ['src/test/test_foo.py']
        mock_static.return_value = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        smart_selector.main()

        # Verify pytest was called
        mock_run.assert_called_once()
        cmd_called = mock_run.call_args[0][0]
        self.assertIn('pytest', cmd_called)
        self.assertIn('src/test/test_foo.py', cmd_called)
        
        # Verify script exits with 0
        mock_exit.assert_called_once_with(0)

    @patch('src.main.smart_selector.start_http_server')
    @patch('src.main.smart_selector.get_changed_files')
    @patch('src.main.smart_selector.sys.exit')
    def test_main_no_valid_changes(self, mock_exit, mock_get_files, mock_http):
        os.environ['DAEMON_MODE'] = '0'
        mock_get_files.return_value = ['   ', ''] # Only whitespace/empty

        smart_selector.main()

        mock_exit.assert_called_once_with(0)

if __name__ == '__main__':
    unittest.main()

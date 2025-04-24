import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user import User

# Global list to store test results
test_results = []

# Helper function to handle common test logic
def run_test_with_mocked_output(test_function, *args, **kwargs):
    with patch("utils.Utility.clear_screen"):
        with patch("builtins.print") as mock_print:
            result = test_function(*args, **kwargs)
            output_lines = [call.args[0] for call in mock_print.call_args_list]
            cleaned_output = output_lines[0].lstrip('\n') if output_lines else ""
            return result, output_lines, cleaned_output

# Helper function to set up mock database connection
def setup_mock_db(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

# Helper function to log test results
def log_test_result(test_name, output_lines, expected_message):
    if any(expected_message in line for line in output_lines):
        test_results.append([test_name, "\033[92mPASS\033[0m"])
    else:
        test_results.append([test_name, "\033[91mFAIL\033[0m"])

class TestUserFunctional(unittest.TestCase):

    @patch("utils.Utility.display_header")
    @patch("builtins.input", side_effect=["Test Company"])
    @patch("sqlite3.connect")
    def test_employer_sign_up_success(self, mock_connect, mock_input, mock_display_header):
        print("\033[92m\nRunning test_employer_sign_up_success:\033[0m")
        _, mock_cursor = setup_mock_db(mock_connect)
        mock_cursor.fetchone.return_value = None

        result, output_lines, cleaned_output = run_test_with_mocked_output(User.sign_up, "employeruser", "password123", "2")
        log_test_result("test_employer_sign_up_success", output_lines, "Sign-up successful!")
        self.assertIsNotNone(result)

        print(cleaned_output)

    @patch("utils.Utility.display_header")
    @patch("builtins.input", side_effect=["Test Name", "Python, Java", "5 years", "50", "PayPal"])
    @patch("sqlite3.connect")
    def test_freelancer_sign_up_success(self, mock_connect, mock_input, mock_display_header):
        print("\033[92m\nRunning test_freelancer_sign_up_success:\033[0m")
        _, mock_cursor = setup_mock_db(mock_connect)
        mock_cursor.fetchone.return_value = None

        result, output_lines, cleaned_output = run_test_with_mocked_output(User.sign_up, "freelanceruser", "password123", "1")
        log_test_result("test_freelancer_sign_up_success", output_lines, "Sign-up successful!")
        self.assertIsNotNone(result)

        print(cleaned_output)

    @patch("sqlite3.connect")
    def test_login_failure(self, mock_connect):
        print("\033[92m\nRunning test_login_failure:\033[0m")
        _, mock_cursor = setup_mock_db(mock_connect)
        mock_cursor.fetchone.return_value = None

        result, output_lines, cleaned_output = run_test_with_mocked_output(User.login, "wronguser", "wrongpassword")
        log_test_result("test_login_failure", output_lines, "Invalid username or password!")
        self.assertIsNone(result)

        print(cleaned_output)

    @patch("sqlite3.connect")
    def test_login_success(self, mock_connect):
        print("\033[92m\nRunning test_login_success:\033[0m")
        _, mock_cursor = setup_mock_db(mock_connect)
        hashed_password = User(1, "testuser", "password123", "Freelancer").hash_password("password123")
        mock_cursor.fetchone.return_value = (1, "testuser", hashed_password, "Freelancer")

        result, output_lines, cleaned_output = run_test_with_mocked_output(User.login, "testuser", "password123")
        log_test_result("test_login_success", output_lines, "Login successful!")
        self.assertIsNotNone(result)

        print(cleaned_output)

    @patch("sqlite3.connect")
    def test_sign_up_username_taken(self, mock_connect):
        print("\033[92m\nRunning test_sign_up_username_taken:\033[0m")
        _, mock_cursor = setup_mock_db(mock_connect)
        mock_cursor.fetchone.return_value = ("testuser",)

        result, output_lines, cleaned_output = run_test_with_mocked_output(User.sign_up, "testuser", "password123", "1")
        log_test_result("test_sign_up_username_taken", output_lines, "Username already taken!")
        self.assertIsNone(result)

        print(cleaned_output)

if __name__ == "__main__":
    # Suppress default unittest output except for custom print statements
    unittest.main(exit=False, verbosity=0, testRunner=unittest.TextTestRunner(stream=open(os.devnull, 'w')))

    CYAN = "\033[96m"
    RESET = "\033[0m"

    # Print test results in a table format
    print("\nTest Results:")
    print("┏" + "━" * 37 + "┳" + "━" * 8 + "┓")
    print(f"┃ {CYAN}FUNCTION NAME{RESET:<26} ┃ {CYAN}STATUS{RESET:<4} ┃")
    print("┣" + "━" * 37 + "╋" + "━" * 8 + "┫")
    for result in test_results:
        print(f"┃ {result[0]:<35} ┃ {result[1]:<15} ┃")
    print("┗" + "━" * 37 + "┻" + "━" * 8 + "┛")
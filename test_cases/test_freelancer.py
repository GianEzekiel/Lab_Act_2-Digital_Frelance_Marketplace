import unittest
import sqlite3
from unittest.mock import patch, MagicMock
import os
import sys
import contextlib

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from freelancer import Freelancer

class TestFreelancer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = ":memory:"  # Use in-memory database for faster tests
        # Create the database connection once for all tests
        cls.conn = sqlite3.connect(cls.test_db)
        cls.cursor = cls.conn.cursor()
       
        # Create the table once
        cls.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                name TEXT,
                skills TEXT,
                experience TEXT,
                hourly_rate REAL,
                payment_method TEXT
            )
        ''')
        cls.conn.commit()

    def setUp(self):
        # Clear and reinitialize test data before each test
        self.cursor.execute('DELETE FROM users')
        self.cursor.execute('''
            INSERT INTO users (username, password, role, name, skills, experience, hourly_rate, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('testuser', 'password123', 'freelancer', 'Test User', 'Python, SQL', '5 years', 50.0, 'PayPal'))
        self.conn.commit()

        self.freelancer = Freelancer(
            id=1,
            username='testuser',
            password='password123',
            role='freelancer',
            name='Test User',
            skills='Python, SQL',
            experience='5 years',
            hourly_rate=50.0,
            payment_method='PayPal'
        )

    def tearDown(self):
        # Clear the table after each test
        self.cursor.execute('DELETE FROM users')
        self.conn.commit()

    @classmethod
    def tearDownClass(cls):
        # Close the connection after all tests
        cls.conn.close()

    def run(self, result=None):
        """Override run method to display test results."""
        result = result or self.defaultTestResult()
        super().run(result)
        test_name = self._testMethodName.replace("test_", "").replace("_", " ").title()
        if result.wasSuccessful():
            print(f"{test_name}: PASSED")
        else:
            print(f"{test_name}: FAILED")
            for failed_test, reason in result.failures + result.errors:
                if failed_test == self:
                    print(f"Reason:\n{reason}")

    def test_view_profile(self):
        """Test that profile information can be retrieved correctly"""
        self.cursor.execute(
            "SELECT name, skills, experience, hourly_rate, payment_method FROM users WHERE username = ?",
            (self.freelancer.username,)
        )
        profile = self.cursor.fetchone()

        self.assertIsNotNone(profile, "Profile should exist for test user")
        self.assertEqual(profile[0], 'Test User', "Name should match")
        self.assertEqual(profile[1], 'Python, SQL', "Skills should match")
        self.assertEqual(profile[2], '5 years', "Experience should match")
        self.assertEqual(profile[3], 50.0, "Hourly rate should match")
        self.assertEqual(profile[4], 'PayPal', "Payment method should match")

    def test_edit_name(self):
        """Test that name can be updated successfully"""
        new_name = "Updated Test User"
       
        self.cursor.execute(
            "UPDATE users SET name = ? WHERE username = ?",
            (new_name, self.freelancer.username)
        )
        self.conn.commit()
       
        self.cursor.execute(
            "SELECT name FROM users WHERE username = ?",
            (self.freelancer.username,)
        )
        updated_name = self.cursor.fetchone()[0]

        self.assertEqual(updated_name, new_name, "Name should be updated in database")
       
    def test_edit_name_through_class(self):
        """Test that name can be updated through Freelancer class"""
        new_name = "Updated Test User"
       
        # Call the actual method on the Freelancer instance
        self.freelancer.update_name(new_name, self.conn)
       
        # Verify the change in the database
        self.cursor.execute(
            "SELECT name FROM users WHERE username = ?",
            (self.freelancer.username,)
        )
        updated_name = self.cursor.fetchone()[0]

        self.assertEqual(updated_name, new_name, "Name should be updated in database")

    def test_edit_hourly_rate_valid(self):
        """Test that hourly rate can be updated with valid values"""
        new_rate = 75.0
       
        self.cursor.execute(
            "UPDATE users SET hourly_rate = ? WHERE username = ?",
            (new_rate, self.freelancer.username)
        )
        self.conn.commit()
       
        self.cursor.execute(
            "SELECT hourly_rate FROM users WHERE username = ?",
            (self.freelancer.username,)
        )
        updated_rate = self.cursor.fetchone()[0]

        self.assertEqual(updated_rate, new_rate, "Hourly rate should be updated")

    def test_edit_hourly_rate_invalid(self):
        """Test that invalid hourly rates are rejected"""
        invalid_rates = [-10.0, 0.0, "not_a_number", None]

        for rate in invalid_rates:
            with self.subTest(rate=rate):
                with self.assertRaises(ValueError):
                    self.freelancer.update_hourly_rate(rate, self.conn)

    def test_edit_skills(self):
        """Test that skills can be updated"""
        new_skills = "Python, SQL, JavaScript"
       
        self.cursor.execute(
            "UPDATE users SET skills = ? WHERE username = ?",
            (new_skills, self.freelancer.username)
        )
        self.conn.commit()
       
        self.cursor.execute(
            "SELECT skills FROM users WHERE username = ?",
            (self.freelancer.username,)
        )
        updated_skills = self.cursor.fetchone()[0]

        self.assertEqual(updated_skills, new_skills, "Skills should be updated")

    def test_profile_not_found(self):
        """Test handling of non-existent profiles"""
        self.cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            ('nonexistent_user',)
        )
        profile = self.cursor.fetchone()
        self.assertIsNone(profile, "Should return None for non-existent user")

    @patch('sqlite3.connect')
    def test_database_error_handling(self, mock_connect):
        """Test that database errors are handled gracefully"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.DatabaseError("Test error")
        
        with self.assertRaises(sqlite3.DatabaseError):
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            conn.close()
            class TestSubmitMilestone(unittest.TestCase):
                def setUp(self):
                    # Set up in-memory database and mock data
                    self.conn = sqlite3.connect(":memory:")
                    self.cursor = self.conn.cursor()
                    self.cursor.execute('''
                        CREATE TABLE milestones (
                            id INTEGER PRIMARY KEY,
                            job_id INTEGER,
                            freelancer_id INTEGER,
                            title TEXT,
                            status TEXT
                        )
                    ''')
                    self.conn.commit()

                    # Insert mock milestone data
                    self.cursor.execute('''
                        INSERT INTO milestones (job_id, freelancer_id, title, status)
                        VALUES (?, ?, ?, ?)
                    ''', (1, 1, "Milestone 1", "in progress"))
                    self.conn.commit()

                    # Create Freelancer instance
                    self.freelancer = Freelancer(
                        id=1,
                        username="testuser",
                        password="password123",
                        role="freelancer"
                    )

                def tearDown(self):
                    self.conn.close()

                @patch("builtins.input", side_effect=["Milestone 1"])
                @patch("sqlite3.connect")
                def test_submit_milestone_success(self, mock_connect, mock_input):
                    """Test successful submission of a milestone."""
                    mock_connect.return_value = self.conn

                    with patch("time.sleep"), patch("builtins.print") as mock_print:
                        self.freelancer.submit_milestone("Milestone 1")

                    # Verify database update
                    self.cursor.execute("SELECT status FROM milestones WHERE title = ?", ("Milestone 1",))
                    status = self.cursor.fetchone()[0]
                    self.assertEqual(status, "for approval", "Milestone status should be updated to 'for approval'.")

                    # Verify output
                    mock_print.assert_any_call("Submitting 'Milestone 1' for approval...")

                @patch("builtins.input", side_effect=["Nonexistent Milestone"])
                @patch("sqlite3.connect")
                def test_submit_milestone_not_found(self, mock_connect, mock_input):
                    """Test submission of a non-existent milestone."""
                    mock_connect.return_value = self.conn

                    with patch("time.sleep"), patch("builtins.print") as mock_print:
                        self.freelancer.submit_milestone("Nonexistent Milestone")

                    # Verify output
                    mock_print.assert_any_call("Error: Milestone 'Nonexistent Milestone' not found or does not belong to you.")

                @patch("builtins.input", side_effect=["Milestone 1"])
                @patch("sqlite3.connect")
                def test_submit_milestone_already_approved(self, mock_connect, mock_input):
                    """Test submission of an already approved milestone."""
                    mock_connect.return_value = self.conn

                    # Update milestone status to 'approved'
                    self.cursor.execute("UPDATE milestones SET status = 'approved' WHERE title = ?", ("Milestone 1",))
                    self.conn.commit()

                    with patch("time.sleep"), patch("builtins.print") as mock_print:
                        self.freelancer.submit_milestone("Milestone 1")

                    # Verify output
                    mock_print.assert_any_call("This milestone has already been approved.")

                @patch("builtins.input", side_effect=["Milestone 1"])
                @patch("sqlite3.connect")
                def test_submit_milestone_already_for_approval(self, mock_connect, mock_input):
                    """Test submission of a milestone already waiting for approval."""
                    mock_connect.return_value = self.conn

                    # Update milestone status to 'for approval'
                    self.cursor.execute("UPDATE milestones SET status = 'for approval' WHERE title = ?", ("Milestone 1",))
                    self.conn.commit()

                    with patch("time.sleep"), patch("builtins.print") as mock_print:
                        self.freelancer.submit_milestone("Milestone 1")
                    # Verify output
                    mock_print.assert_any_call("This milestone is already waiting for employer approval.")

if __name__ == '__main__':
    CYAN = "\033[96m"
    RESET = "\033[0m"

    class CustomTestResult(unittest.TextTestResult):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.test_results = []

        def addSuccess(self, test):
            super().addSuccess(test)
            name = test._testMethodName.replace("test_", "").replace("_", " ").title()
            self.test_results.append((name, "PASSED"))

        def addFailure(self, test, err):
            super().addFailure(test, err)
            name = test._testMethodName.replace("test_", "").replace("_", " ").title()
            self.test_results.append((name, "FAILED"))

        def addError(self, test, err):
            super().addError(test, err)
            name = test._testMethodName.replace("test_", "").replace("_", " ").title()
            self.test_results.append((name, "ERROR"))

    class CustomTestRunner(unittest.TextTestRunner):
        def _makeResult(self):
            return CustomTestResult(self.stream, self.descriptions, self.verbosity)

        def run(self, test):
            result = super().run(test)
            # Display table
            print("\nTest Results:")
            print("┏" + "━" * 37 + "┳" + "━" * 15 + "┓")
            print(f"┃ {CYAN}FUNCTION NAME{RESET:<26} ┃ {CYAN}STATUS{RESET:<11} ┃")
            print("┣" + "━" * 37 + "╋" + "━" * 15 + "┫")
            for name, status in result.test_results:
                print(f"┃ {name:<35} ┃ {status:<13} ┃")
            print("┗" + "━" * 37 + "┻" + "━" * 15 + "┛")
            return result

    unittest.main(testRunner=CustomTestRunner(verbosity=0))


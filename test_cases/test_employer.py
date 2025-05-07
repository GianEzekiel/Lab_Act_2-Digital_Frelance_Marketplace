import unittest
import sqlite3
import os
import sys

# Allow importing from parent directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from employer import Employer
from utils import Utility
import job_system

# Mock utility methods
Utility.clear_screen = lambda: None
Utility.display_header = lambda title: print(f"\n=== {title} ===")
Utility.divider = lambda: print("-" * 30)


class TestEmployerFunctions(unittest.TestCase):
    test_results = []

    @classmethod
    def setUpClass(cls):
        cls.db_name = "freelancer_marketplace.db"
        cls.conn = sqlite3.connect(cls.db_name)
        cls.cursor = cls.conn.cursor()

    def setUp(self):
        self._reset_database()

    def _reset_database(self):
        self.cursor.executescript("""
            DROP TABLE IF EXISTS users;
            DROP TABLE IF EXISTS jobs;
            DROP TABLE IF EXISTS job_applications;
            DROP TABLE IF EXISTS wallet;
            DROP TABLE IF EXISTS milestones;
            DROP TABLE IF EXISTS temporary_wallet;

            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                role TEXT,
                name TEXT,
                skills TEXT,
                experience TEXT,
                hourly_rate REAL
            );

            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY,
                employer_id INTEGER,
                title TEXT,
                description TEXT,
                budget REAL,
                skills_required TEXT,
                duration TEXT,
                status TEXT
            );

            CREATE TABLE job_applications (
                id INTEGER PRIMARY KEY,
                job_id INTEGER,
                freelancer_id INTEGER,
                status TEXT
            );

            CREATE TABLE wallet (
                user_id INTEGER PRIMARY KEY,
                balance REAL
            );

            CREATE TABLE milestones (
                id INTEGER PRIMARY KEY,
                job_id INTEGER,
                freelancer_id INTEGER,
                title TEXT,
                status TEXT,
                payment REAL
            );

            CREATE TABLE temporary_wallet (
                freelancer_id INTEGER PRIMARY KEY,
                employer_id INTEGER,
                balance REAL
            );
        """)

        # Insert test users and wallet balances
        self.cursor.execute("INSERT INTO users (id, username, password, role, name) VALUES (1, 'employer1', 'pass', 'employer', 'Employer One')")
        self.cursor.execute("INSERT INTO users (id, username, password, role, name, skills, experience, hourly_rate) VALUES (2, 'freelancer1', 'pass', 'freelancer', 'Freelancer One', 'Python, SQL', '3 years', 20.0)")
        self.cursor.execute("INSERT INTO wallet (user_id, balance) VALUES (1, 1000.0)")
        self.cursor.execute("INSERT INTO wallet (user_id, balance) VALUES (2, 0.0)")
        self.conn.commit()

    def test_post_job(self):
        try:
            employer = Employer(1, 'employer1', 'pass', 'employer', name='Employer One')
            job = employer.post_job("Test Job", "Test Description", 500.0, "Python", "1 week")
            self.assertIsNotNone(job)
            self.__class__.test_results.append(("test_post_job", "PASS"))
        except Exception as e:
            self.__class__.test_results.append(("test_post_job", f"FAIL: {e}"))
            raise

    def test_view_posted_jobs(self):
        try:
            employer = Employer(1, 'employer1', 'pass', 'employer')
            employer.view_posted_jobs()
            self.__class__.test_results.append(("test_view_posted_jobs", "PASS"))
        except Exception as e:
            self.__class__.test_results.append(("test_view_posted_jobs", f"FAIL: {e}"))
            raise

    def test_add_and_approve_milestone(self):
        print("\nRunning test_add_and_approve_milestone:")
        try:
            employer = Employer(1, 'employer1', 'pass', 'employer')
            # Avoid posting a job again here if the job already exists
            job = employer.post_job("Milestone Job", "Milestone Desc", 300, "SQL", "2 weeks")

            conn = sqlite3.connect("freelancer_marketplace.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO job_applications (job_id, freelancer_id, status) VALUES (?, ?, 'accepted')", (job.id, 2))
            conn.commit()
            conn.close()

            employer.add_milestone(job.id, "First Milestone", 200)
            employer.approve_milestone("First Milestone")

            conn = sqlite3.connect("freelancer_marketplace.db")
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM wallet WHERE user_id = 2")
            freelancer_balance = cursor.fetchone()[0]
            conn.close()

            assert freelancer_balance == 200
            print("✅ Milestone approved and payment recorded correctly.")
            self.__class__.test_results.append(("test_add_and_approve_milestone", "PASS"))
        except Exception as e:
            print(f"❌ Milestone test failed: {e}")
            self.__class__.test_results.append(("test_add_and_approve_milestone", f"FAIL: {str(e)}"))


    def test_finalize_payment(self):
        print("\nRunning test_finalize_payment:")
        try:
            employer = Employer(1, 'employer1', 'pass', 'employer')
            # Avoid posting a job again here if the job already exists
            job = employer.post_job("Milestone Job", "Milestone Desc", 300, "SQL", "2 weeks")

            conn = sqlite3.connect("freelancer_marketplace.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO job_applications (job_id, freelancer_id, status) VALUES (?, ?, 'accepted')", (job.id, 2))
            cursor.execute("INSERT INTO milestones (job_id, freelancer_id, title, status, payment) VALUES (?, ?, ?, 'approved', ?)", (job.id, 2, "Last Milestone", 200))
            cursor.execute("INSERT INTO temporary_wallet (freelancer_id, employer_id, balance) VALUES (2, 1, 200)")
            conn.commit()

            employer.finalize_payment(2, job.id, conn, cursor)

            cursor.execute("SELECT balance FROM wallet WHERE user_id = 2")
            balance = cursor.fetchone()[0]
            conn.close()

            assert balance >= 200
            print("✅ Final payment successfully transferred to freelancer.")
            self.__class__.test_results.append(("test_finalize_payment", "PASS"))
        except Exception as e:
            print(f"❌ Final payment test failed: {e}")
            self.__class__.test_results.append(("test_finalize_payment", f"FAIL: {str(e)}"))

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        cls.print_test_results()

    @classmethod
    def print_test_results(cls):
        CYAN = "\033[96m"
        RESET = "\033[0m"

        print("\nTest Results:")
        print("┏" + "━" * 37 + "┳" + "━" * 15 + "┓")
        print(f"┃ {CYAN}FUNCTION NAME{RESET:<26} ┃ {CYAN}STATUS{RESET:<11} ┃")
        print("┣" + "━" * 37 + "╋" + "━" * 15 + "┫")
        for result in cls.test_results:
            print(f"┃ {result[0]:<35} ┃ {result[1]:<13} ┃")
        print("┗" + "━" * 37 + "┻" + "━" * 15 + "┛")


if __name__ == '__main__':
    unittest.main()

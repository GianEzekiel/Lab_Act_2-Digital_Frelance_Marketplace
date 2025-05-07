import unittest
import time
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_system import Job, Application
from freelancer import Freelancer

# Color definitions
CYAN = "\033[96m"
RESET = "\033[0m"

class TestJobSystem(unittest.TestCase):
    def setUp(self):
        self.freelancer = Freelancer(
            id=1,
            username='freelancer1',
            password='pass',
            role='freelancer',
            name='John Doe',
            skills='Python,SQL',
            experience='3 years',
            hourly_rate=45.0,
            payment_method='PayPal'
        )

        self.job = Job(
            title="Build API",
            description="Develop a RESTful API",
            budget=1000,
            skillrequired="Python",
            duration="2 weeks"
        )

    def test_add_applicant_valid(self):
        """Test adding a valid freelancer as an applicant"""
        self.job.add_applicant(self.freelancer)
        self.assertIn(self.freelancer, self.job.applicants)

    def test_add_applicant_invalid(self):
        """Test adding a non-Freelancer object raises TypeError"""
        with self.assertRaises(TypeError):
            self.job.add_applicant("NotAFreelancer")

    def test_create_application_valid(self):
        """Test successful creation of an application"""
        app = Application(self.freelancer, self.job)
        self.assertEqual(app.freelancer, self.freelancer)
        self.assertEqual(app.job, self.job)
        self.assertEqual(app.status, "applied")

    def test_create_application_invalid_freelancer(self):
        """Test creating application with invalid freelancer"""
        with self.assertRaises(TypeError):
            Application("NotAFreelancer", self.job)

    def test_create_application_invalid_job(self):
        """Test creating application with invalid job"""
        with self.assertRaises(TypeError):
            Application(self.freelancer, "NotAJob")

    def test_update_application_status_valid(self):
        """Test updating application status with valid value"""
        app = Application(self.freelancer, self.job)
        app.update_status("accepted")
        self.assertEqual(app.status, "accepted")

    def test_update_application_status_invalid(self):
        """Test updating application status with invalid value"""
        app = Application(self.freelancer, self.job)
        with self.assertRaises(ValueError):
            app.update_status("unknown_status")




if __name__ == '__main__':
    
    # Custom Test Result and Runner for Colored Output
    class CustomTestResult(unittest.TextTestResult):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.test_results = []
            self.start_time = 0
            self.stop_time = 0

        def startTestRun(self):
            self.start_time = time.time()
            super().startTestRun()

        def stopTestRun(self):
            self.stop_time = time.time()
            super().stopTestRun()

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
            result = self._makeResult()
            result.startTestRun()
            test(result)
            result.stopTestRun()

            # Print custom summary before default output
            for name, status in result.test_results:
                print(f"{name}: {status}")

            # Print standard unittest summary manually
            self.stream.writeln()
            self.stream.writeln("=" * 70)
            run_time = result.stop_time - result.start_time
            self.stream.writeln(f"Ran {result.testsRun} test{'s' if result.testsRun != 1 else ''} in {run_time:.3f}s\n")
            
            print("\nTest Results:")
            print("┏" + "━" * 39 + "┳" + "━" * 15 + "┓")
            print(f"┃ {CYAN}FUNCTION NAME{RESET:<28} ┃ {CYAN}STATUS{RESET:<11} ┃")
            print("┣" + "━" * 39 + "╋" + "━" * 15 + "┫")
            for name, status in result.test_results:
                print(f"┃ {name:<37} ┃ {status:<13} ┃")
            print("┗" + "━" * 39 + "┻" + "━" * 15 + "┛")

            if not result.wasSuccessful():
                self.stream.writeln("FAILED")
            else:
                self.stream.writeln("OK")

            return result

    unittest.main(testRunner=CustomTestRunner(verbosity=0))

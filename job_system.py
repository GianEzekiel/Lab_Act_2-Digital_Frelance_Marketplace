import sqlite3
from freelancer import Freelancer # Ensure Freelancer class exists in main.py
from utils import Utility

class Job:
    def __init__(self, title, description, budget, skillrequired, duration, applicants=None):
        self.title = title
        self.description = description  # Fixed the typo
        self.budget = budget
        self.skillrequired = skillrequired
        self.duration = duration
        self.applicants = applicants if applicants is not None else []  # Default to an empty list
        
    def add_applicant(self, freelancer):
        if isinstance(freelancer, Freelancer):
            self.applicants.append(freelancer)
        else:
            raise TypeError("Applicant must be a Freelancer instance")

class Application:
    def __init__(self, freelancer, job, status="applied"):
        if not isinstance(freelancer, Freelancer):
            raise TypeError("Freelancer must be an instance of Freelancer class")
        if not isinstance(job, Job):
            raise TypeError("Job must be an instance of Job class")
        
        self.freelancer = freelancer
        self.job = job
        self.status = status
    
    def update_status(self, new_status):
        allowed_statuses = ["applied", "accepted", "rejected", "in_progress", "completed"]
        if new_status in allowed_statuses:
            self.status = new_status
        else:
            raise ValueError("Invalid status update")
        
    @staticmethod
    def display_all_applications():
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT job_applications.id, jobs.title, users.username, job_applications.status
            FROM job_applications
            JOIN jobs ON job_applications.job_id = jobs.id
            JOIN users ON job_applications.freelancer_id = users.id
        """)
        applications = cursor.fetchall()
        conn.close()
        
        Utility.display_header("Job Applications")
        for app in applications:
            print(app)
        Utility.divider()
        
    
        

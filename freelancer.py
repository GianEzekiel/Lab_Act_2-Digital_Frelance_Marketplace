import time
from user import User
import sqlite3
from utils import Utility

class Freelancer(User):
    def __init__(self, id, username, password, role, name=None, skills=None, experience=None, hourly_rate=None, payment_method=None, company_name=None):
        super().__init__(id, username, password, role)  # Pass common attributes to the parent class
        self.name = name
        self.skills = skills.split(", ") if skills else []
        self.experience = experience
        self.hourly_rate = hourly_rate
        self.payment_method = payment_method

    def browse_jobs(self):
        """Fetch and display all jobs, then allow freelancer to search or apply."""
        while True:  # Keeps the user in the job browsing section until they choose to exit
            conn = sqlite3.connect("freelancer_marketplace.db")
            cursor = conn.cursor()
            # Fetch all jobs from the database
            cursor.execute("""
                SELECT id, title, description, budget, skills_required, duration
                FROM jobs
            """)
            jobs = cursor.fetchall()
            conn.close()

            if not jobs:
                print("No jobs available at the moment.")
                return  # Only return if no jobs are available

            # Display all jobs
            Utility.clear_screen()
            Utility.display_header("Available Jobs")
            for index, job in enumerate(jobs):
                job_id, title, description, budget, skills_required, duration = job
                print(f"[{job_id}] Title: {title}")
                print(f"    Description: {description}")
                print(f"    Budget: ${budget}")
                print(f"    Skills Required: {skills_required}")
                print(f"    Duration: {duration}")

                # Only print divider if it's not the last job
                if index < len(jobs) - 1:
                    Utility.divider()

            choice = Utility.display_menu("Menu", ["Apply Job", "Exit to Dashboard"])

            if choice == "1":
                self.apply_job()
            elif choice == "2":
                print("Returning to freelancer dashboard...")
                break  # Exits the loop and returns to the freelancer dashboard
            else:
                print("\nInvalid choice. Please try again!")
                time.sleep(1.5)

    # Function to apply for a job
    def apply_job(self):
        """Apply for a job based on the job title."""
        job_title = input("Enter the job title you want to apply for: ").strip()

        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        # Find the job ID based on the title
        cursor.execute("SELECT id FROM jobs WHERE title LIKE ?", ('%' + job_title + '%',))
        job = cursor.fetchone()

        Utility.clear_screen()
        Utility.display_header("Apply Job")

        if not job:
            print("Job not found. Please try again.")
            Utility.divider()
        else:
            job_id = job[0]

            # Insert application into the database
            cursor.execute("""
                INSERT INTO job_applications (job_id, freelancer_id, status)
                VALUES (?, ?, 'applied')
            """, (job_id, self.id))

            conn.commit()
            print(f"Applied for '{job_title}' successfully!")
            Utility.divider()

        conn.close()
        input("Press Enter to Return...")  # Prevents instant return
       
    def track_applications(self):
        """Fetch and display job applications for the freelancer."""
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        # Fetch applications submitted by this freelancer
        cursor.execute("""
            SELECT ja.id, j.title, j.budget, ja.status
            FROM job_applications ja
            JOIN jobs j ON ja.job_id = j.id
            WHERE ja.freelancer_id = ?
        """, (self.id,))
       
        applications = cursor.fetchall()
        conn.close()

        if not applications:
            print("You have not applied to any jobs yet.")
            return

        Utility.clear_screen()
        Utility.display_header("Job Applications")
        for app_id, title, budget, status in applications:
            print(f"Application ID: {app_id}")
            print(f"Job Title: {title}")
            print(f"Budget: ${budget}")
            print(f"Status: {status}")
            Utility.divider()
       
        input("Press Enter to Return...")
   
    def edit_profile(self):
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()
        Utility.display_header("Edit Profile")
        print(f"[1] Name: {self.name}\n[2] Skills: {self.skills}\n[3] Experience: {self.experience}\n[4] Hourly Rate: ${self.hourly_rate}\n[5] Payment Method: {self.payment_method}")
        choice = input("Select field to edit [1-5] or [6] Back: ")
       
        if choice == "1":
            self.name = input("Enter new name: ")
            cursor.execute("UPDATE users SET name = ? WHERE username = ?", (self.name, self.username))
        elif choice == "2":
            self.skills = input("Enter new skills (comma separated): ")
            cursor.execute("UPDATE users SET skills = ? WHERE username = ?", (self.skills, self.username))
        elif choice == "3":
            self.experience = input("Enter new experience: ")
            cursor.execute("UPDATE users SET experience = ? WHERE username = ?", (self.experience, self.username))
        elif choice == "4":
            self.hourly_rate = float(input("Enter new hourly rate: "))
            cursor.execute("UPDATE users SET hourly_rate = ? WHERE username = ?", (self.hourly_rate, self.username))
        elif choice == "5":
            self.payment_method = input("Enter new payment method: ")
            cursor.execute("UPDATE users SET payment_method = ? WHERE username = ?", (self.payment_method, self.username))
        elif choice == "6":
            Utility.clear_screen()
            return
       
        conn.commit()
        conn.close()
        print("Profile updated successfully!")
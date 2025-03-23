import os
import time
from payment_system import Wallet
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
        self.wallet = Wallet(id)

    def browse_jobs(self):
        """Fetch and display all available jobs, excluding those in progress."""
        while True:
            conn = sqlite3.connect("freelancer_marketplace.db")
            cursor = conn.cursor()

            # Fetch only jobs that are still open
            cursor.execute("""
                SELECT id, title, description, budget, skills_required, duration
                FROM jobs
                WHERE status = 'open'  -- Only fetch jobs that are not in progress
            """)
            jobs = cursor.fetchall()
            conn.close()

            if not jobs:
                print("\nNo jobs available at the moment.")
                time.sleep(1.5)
                return  # Exit if no jobs are available

            # Display available jobs
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

            choice = Utility.display_menu("Options", ["Apply Job", "Back"], use_header=False)

            if choice == "1":
                self.apply_job()
            elif choice == "2":
                print("Returning to freelancer dashboard...")
                break
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
            print(f"\nApplied for '{job_title}' successfully!\n")

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
            print("\nYou have not applied to any jobs yet.")
            time.sleep(1.5)
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

    def submit_milestone(self, milestone_title):
        """Submits a milestone for approval based on the provided milestone title."""

        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        # 🔍 Fetch milestone based on the provided title
        cursor.execute('''
            SELECT job_id, status FROM milestones
            WHERE freelancer_id = ? AND title = ?
        ''', (self.id, milestone_title))

        milestone = cursor.fetchone()

        if not milestone:
            print(f"Error: Milestone '{milestone_title}' not found or does not belong to you.")
            time.sleep(1.5)
            conn.close()
            return

        job_id, status = milestone

        print(f"DEBUG: Found milestone '{milestone_title}' with status '{status}'")  # Debugging

        if status == "approved":
            print("This milestone has already been approved.")
        elif status == "for approval":
            print("This milestone is already waiting for employer approval.")
        else:
            # Update status to "for approval"
            cursor.execute('''
                UPDATE milestones
                SET status = 'for approval'
                WHERE job_id = ? AND freelancer_id = ? AND title = ?
            ''', (job_id, self.id, milestone_title))

            conn.commit()
            print(f"Submitting '{milestone_title}' for approval...")

        time.sleep(1.5)
        conn.close()

    def view_and_edit_profile(self):
        """View and edit freelancer profile."""
       
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        # Fetch current profile details from the database
        cursor.execute("SELECT name, skills, experience, hourly_rate, payment_method FROM users WHERE username = ?", (self.username,))
        profile = cursor.fetchone()

        if not profile:
            print("Error: Profile not found.")
            time.sleep(1.5)
            conn.close()
            return

        # Unpacking profile details
        name, skills, experience, hourly_rate, payment_method = profile

        # Display current profile details
        Utility.clear_screen()
        Utility.display_header("Edit Profile")
        print(f"[1] Name: {name}")
        print(f"[2] Skills: {skills}")
        print(f"[3] Experience: {experience}")
        print(f"[4] Hourly Rate: ${hourly_rate}")
        print(f"[5] Payment Method: {payment_method}")
        print("[6] Go Back")
        Utility.divider()
        choice = input("Select field to edit [1-5] or [6] to go back: ").strip()

        # Editing selected field
        if choice == "1":
            new_name = input("Enter new name: ").strip()
            cursor.execute("UPDATE users SET name = ? WHERE username = ?", (new_name, self.username))
            self.name = new_name  # Update object attribute
        elif choice == "2":
            new_skills = input("Enter new skills (comma separated): ").strip()
            cursor.execute("UPDATE users SET skills = ? WHERE username = ?", (new_skills, self.username))
            self.skills = new_skills  # Update object attribute
        elif choice == "3":
            new_experience = input("Enter new experience: ").strip()
            cursor.execute("UPDATE users SET experience = ? WHERE username = ?", (new_experience, self.username))
            self.experience = new_experience  # Update object attribute
        elif choice == "4":
            try:
                new_hourly_rate = float(input("Enter new hourly rate: ").strip())
                cursor.execute("UPDATE users SET hourly_rate = ? WHERE username = ?", (new_hourly_rate, self.username))
                self.hourly_rate = new_hourly_rate  # Update object attribute
            except ValueError:
                print("Invalid input. Hourly rate must be a number.")
        elif choice == "5":
            new_payment_method = input("Enter new payment method: ").strip()
            cursor.execute("UPDATE users SET payment_method = ? WHERE username = ?", (new_payment_method, self.username))
            self.payment_method = new_payment_method  # Update object attribute
        elif choice == "6":
            print("Returning to the main menu.")
            conn.close()
            return
        else:
            print("\nInvalid choice. Please select a valid option.")
            time.sleep(1.5)

        # Commit changes and close connection
        conn.commit()
        conn.close()
       
        print("\nProfile updated successfully!")
        time.sleep(1.5)
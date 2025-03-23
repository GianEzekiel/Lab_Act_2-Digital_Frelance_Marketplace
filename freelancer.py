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
   
    def work_in_progress(self):
            """Display work in progress and allow freelancer to submit work."""
        
            conn = sqlite3.connect("freelancer_marketplace.db")
            cursor = conn.cursor()

            # Fetch jobs where freelancer has been accepted and is working
            cursor.execute('''
                SELECT jobs.id, jobs.title
                FROM jobs
                JOIN job_applications ON jobs.id = job_applications.job_id
                WHERE job_applications.freelancer_id = ? AND job_applications.status = 'accepted'
                AND jobs.status = 'in_progress'
            ''', (self.id,))

            jobs = cursor.fetchall()

            if not jobs:
                print("No active jobs found.")
                conn.close()
                return

            # Display jobs
            print("\nSelect a job:")
            for idx, (job_id, job_title) in enumerate(jobs, 1):
                print(f"[{idx}] {job_title}")

            try:
                choice = int(input("Enter job number: "))
                job_id = jobs[choice - 1][0]  # Get selected job_id
            except (ValueError, IndexError):
                print("Invalid selection.")
                conn.close()
                return

            # Fetch milestones for the selected job
            cursor.execute('''
                SELECT title, payment, status
                FROM milestones
                WHERE job_id = ? AND freelancer_id = ?
            ''', (job_id, self.id))

            milestones = cursor.fetchall()

            if not milestones:
                print("No milestones found for this job.")
                conn.close()
                return

            os.system("cls")  # Clear screen for better display
            print("=" * 40)
            print(" " * 10 + "Work in Progress")
            print("=" * 40)
            print(f"Job: {jobs[choice - 1][1]}")
            print("\nMilestones:")

            for idx, (title, payment, status) in enumerate(milestones, 1):
                print(f"[{idx}] {title} (Php {payment}) [{status}]")

            submit = input("\nSubmit Work? [Y/N]: ").strip().lower()
            if submit == "y":
                self.submit_milestone(job_id)

            conn.close()

    def submit_milestone(self, job_id):
        """Freelancer picks a milestone to submit for approval using the milestone title."""
    
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        # Fetch milestones for the freelancer
        cursor.execute('''
            SELECT title, payment, status
            FROM milestones
            WHERE job_id = ? AND freelancer_id = ?
        ''', (job_id, self.id))

        milestones = cursor.fetchall()

        if not milestones:
            print("No milestones found for this job.")
            conn.close()
            return

        print("\nSelect a milestone to submit:")
        for idx, (title, amount, status) in enumerate(milestones, 1):
            print(f"[{idx}] {title} (Php {amount}) [{status}]")

        milestone_title = input("\nEnter milestone title to submit: ").strip()

        # Check if the milestone exists
        cursor.execute('''
            SELECT status FROM milestones
            WHERE job_id = ? AND freelancer_id = ? AND title = ?
        ''', (job_id, self.id, milestone_title))

        milestone = cursor.fetchone()

        if not milestone:
            print("Error: Milestone not found or does not belong to you.")
        else:
            status = milestone[0]
        
            if status == "Complete":
                print("This milestone has already been completed.")
            else:
                # Update status to "Pending Approval"
                cursor.execute('''
                    UPDATE milestones
                    SET status = 'Pending Approval'
                    WHERE job_id = ? AND freelancer_id = ? AND title = ?
                ''', (job_id, self.id, milestone_title))

                conn.commit()
                print(f"Submitting '{milestone_title}' for approval...")
        conn.close()

    def wallet_menu(self):
        """Handles wallet balance and payment settings."""
        if not hasattr(self, "wallet"):  # Ensure wallet is initialized
            self.wallet = Wallet(self.username)

        while True:
            os.system("cls")
            self.wallet.balance = self.wallet.get_balance_from_db()  # ✅ Refresh balance from DB
            print("\n--- Wallet & Payment Settings ---")
            print(f"Current Balance: Php {self.wallet.balance:.2f}")
            print("[1] Deposit Funds\n[2] Withdraw Funds\n[3] View Payment History\n[4] Back")

            choice = input("Select an option: ").strip()

            if choice == "1":
                try:
                    amount = float(input("Enter deposit amount: "))
                    if amount > 0:
                        self.wallet.deposit(amount)
                    else:
                        print("Deposit amount must be greater than zero!")
                except ValueError:
                    print("Invalid input! Please enter a valid number.")
        
            elif choice == "2":
                try:
                    amount = float(input("Enter withdrawal amount: "))
                    if amount > 0:
                        self.wallet.withdraw(amount)
                    else:
                        print("Withdrawal amount must be greater than zero!")
                except ValueError:
                    print("Invalid input! Please enter a valid number.")


            elif choice == "3":
                self.view_payment_history()  # Ensure this function is implemented

            elif choice == "4":
                break

            else:
                print("Invalid choice! Please try again.")
                time.sleep(2)

    def view_and_edit_profile(self):
        """View and edit freelancer profile."""
       
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        # Fetch current profile details from the database
        cursor.execute("SELECT name, skills, experience, hourly_rate, payment_method FROM users WHERE username = ?", (self.username,))
        profile = cursor.fetchone()

        if not profile:
            print("Error: Profile not found.")
            conn.close()
            return

        # Unpacking profile details
        name, skills, experience, hourly_rate, payment_method = profile

        # Display current profile details
        Utility.display_header("Edit Profile")
        print(f"[1] Name: {name}")
        print(f"[2] Skills: {skills}")
        print(f"[3] Experience: {experience}")
        print(f"[4] Hourly Rate: ${hourly_rate}")
        print(f"[5] Payment Method: {payment_method}")
        print("[6] Go Back")

        choice = input("\nSelect field to edit [1-5] or [6] to go back: ").strip()

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
            print("Invalid choice. Please select a valid option.")

        # Commit changes and close connection
        conn.commit()
        conn.close()
       
        print("Profile updated successfully!")
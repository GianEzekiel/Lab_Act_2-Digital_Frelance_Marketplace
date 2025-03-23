import os
import time
import job_system
from payment_system import Wallet
from user import User
import sqlite3
from utils import Utility

class Employer(User):
    def __init__(self, id, username, password, role, name=None, skills=None, experience=None, hourly_rate=None, payment_method=None, company_name=None):
        super().__init__(id, username, password, role)  # Pass common attributes to the parent class
        self.company_name = company_name
        self.posted_jobs = []  # List to store jobs posted by the employer
        self.wallet = Wallet(id)

    def post_job(self, title, description, budget, skill_required, duration):
        """Creates a new job posting, adds it to the database, and returns the Job object."""
       
        # Create Job object in memory
        job = job_system.Job(title, description, budget, skill_required, duration, [])

        # Store job in database
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO jobs (employer_id, title, description, budget, skills_required, duration, status)
            VALUES (?, ?, ?, ?, ?, ?, 'open')
        """, (self.id, title, description, budget, skill_required, duration))

        # Get the ID of the newly inserted job
        job_id = cursor.lastrowid
        job.id = job_id  # Assign the ID to the job object

        conn.commit()
        conn.close()

        # Add job to employer's posted jobs list
        self.posted_jobs.append(job)

        return job  # Returning the job instance

    def view_applicants(self, job_title):
        """Displays applicants for a job posted by the employer."""

        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        # Check if the employer has posted this job
        cursor.execute("SELECT id FROM jobs WHERE title = ? AND employer_id = ?", (job_title, self.id))
        job_data = cursor.fetchone()

        if not job_data:
            print(f"You haven't posted a job titled '{job_title}'.")
            conn.close()
            return

        job_id = job_data[0]  # Extract job ID

        # Fetch applicants for this job
        cursor.execute("""
            SELECT u.id, u.name, u.skills, u.experience, u.hourly_rate, ja.id
            FROM users u
            JOIN job_applications ja ON u.id = ja.freelancer_id
            WHERE ja.job_id = ? AND ja.status = 'applied'
        """, (job_id,))

        applicants = cursor.fetchall()
        conn.close()

        if not applicants:
            print(f"No applicants for the job '{job_title}' yet.")
            return

        # Manage applicants
        while True:
            # Display applicants
            Utility.clear_screen()
            Utility.display_header(f"Applicants for {job_title}")
            for freelancer_id, name, skills, experience, hourly_rate, application_id in applicants:
                print(f"  Applicant: {name}")  # <-- Freelancer Name instead of ID
                print(f"  Skills: {skills}")
                print(f"  Experience: {experience}")
                print(f"  Hourly Rate: ${hourly_rate:.2f}/hr")
                Utility.divider()
            action = input("Enter Applicant Name or type 'exit': ").strip()

            if action.lower() == "exit":
                break

            applicant = next((app for app in applicants if app[1].lower() == action.lower()), None)

            if not applicant:
                print("\nInvalid Freelancer Name. Try again.")
                time.sleep(1.5)
                continue

            _, name, skills, experience, hourly_rate, application_id = applicant
            self.manage_applicant(application_id, job_id, name, skills, experience, hourly_rate)

    def manage_applicant(self, application_id, job_id, name, skills, experience, hourly_rate):
        """Allows the employer to view the applicant profile and accept/reject them."""

        Utility.clear_screen()
        Utility.display_header(f"{name}'s Profile")
        print(f"  Skills: {skills}")
        print(f"  Experience: {experience}")
        print(f"  Hourly Rate: ${hourly_rate:.2f}/hr")
        Utility.divider()

        # Accept or Reject
        while True:
            decision = input("Accept (A) or Reject (R) this applicant? ").strip().lower()
            if decision in ["a", "r"]:
                new_status = "accepted" if decision == "a" else "rejected"
                print(f"\n{name} has been {'accepted' if decision == 'a' else 'rejected'}.")
                time.sleep(1.5)

                # Update database
                conn = sqlite3.connect("freelancer_marketplace.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE job_applications SET status = ? WHERE id = ?", (new_status, application_id))
                
                if decision == "a":
                    cursor.execute("UPDATE jobs SET status = 'in_progress' WHERE id = ?", (job_id,),
                    )

                
                conn.commit()
                conn.close()
                break
            else:
                print("Invalid input. Please enter 'A' to accept or 'R' to reject.\n")
                
    def add_milestone(self, job_id):
        """Allows an employer to add a milestone for a job."""
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        # Get the accepted freelancer_id for this job
        cursor.execute("SELECT freelancer_id FROM job_applications WHERE job_id = ? AND status = 'accepted'", (job_id,))
        freelancer = cursor.fetchone()

        if not freelancer:
            print("No freelancer has been assigned to this job.")
            conn.close()
            return

        freelancer_id = freelancer[0]

        title = input("Enter milestone title: ")
        payment = float(input("Enter milestone payment: "))

        # Insert new milestone into the table
        cursor.execute('''
            INSERT INTO milestones (job_id, freelancer_id, title, status, payment)
            VALUES (?, ?, ?, 'pending', ?)
        ''', (job_id, freelancer_id, title, payment))

        conn.commit()
        conn.close()

        print("Milestone added successfully!")
       
    def approve_milestone(self, milestone_title):
        """Allows an employer to approve a milestone and transfer funds to the freelancer."""
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()


        # Fetch milestone details including the freelancer_id and payment amount
        cursor.execute("SELECT id, payment, freelancer_id, status FROM milestones WHERE title = ?", (milestone_title,))
        milestone = cursor.fetchone()


        if not milestone:
            print("Error: Milestone not found.")
            conn.close()
            return

        milestone_id, amount, freelancer_id, status = milestone

        if status == "approved":
            print("Milestone is already approved.")
        else:
            # Fetch freelancer wallet using user_id instead of username
            cursor.execute("SELECT balance FROM wallet WHERE user_id = ?", (freelancer_id,))
            freelancer_wallet = cursor.fetchone()


            if not freelancer_wallet:
                print(f"Error: Wallet not found for freelancer with ID {freelancer_id}.")
            else:
                freelancer_balance = freelancer_wallet[0]

                # Transfer funds from employer to freelancer
                if self.wallet.balance >= amount:
                    new_employer_balance = self.wallet.balance - amount
                    new_freelancer_balance = freelancer_balance + amount


                    # Update employer wallet
                    cursor.execute("UPDATE wallet SET balance = ? WHERE user_id = ?", (new_employer_balance, self.user_id))
                   
                    # Update freelancer wallet
                    cursor.execute("UPDATE wallet SET balance = ? WHERE user_id = ?", (new_freelancer_balance, freelancer_id))


                    # Update milestone status
                    cursor.execute("UPDATE milestones SET status = 'approved' WHERE id = ?", (milestone_id,))
                    conn.commit()


                    print(f"Milestone '{milestone_title}' approved! Php {amount} transferred to freelancer ID {freelancer_id}.")
                else:
                    print("Error: Insufficient funds in employer wallet!")

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
       
    def view_posted_jobs(self):
        """Fetch and print all jobs posted by the employer."""
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, description, budget, skills_required, duration, status
            FROM jobs
            WHERE employer_id = ?
        """, (self.id,))

        jobs = cursor.fetchall()
       
        print(f"Debug: Retrieved Jobs = {jobs}")  # Print jobs fetched from the database

        conn.close()

        if not jobs:
            print("Debug: No jobs found in database for this employer.")
            return

        print("\n--- Your Posted Jobs ---")
        for job in jobs:
            job_id, title, description, budget, skills, duration, status = job
            print(f"\nJob ID: {job_id}\nTitle: {title}\nDescription: {description}\nBudget: ${budget}\nSkills Required: {skills}\nDuration: {duration}\nStatus: {status}")
            print("-" * 50)

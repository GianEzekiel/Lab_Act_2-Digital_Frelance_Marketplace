import sqlite3
import hashlib
import os
import time
import job_system
import freelancer_marketplace

# Database Setup
def init_db():
    db_path = os.path.abspath("freelancer_marketplace.db")
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT,
                        name TEXT,
                        skills TEXT,
                        experience TEXT,
                        hourly_rate REAL,
                        payment_method TEXT,
                        company_name TEXT
                    )''')
    conn.commit()
    conn.close()

def display_header(title):
    print("=" * 35)
    print(f"{title.center(35)}")
    print("=" * 35)

def divider():
    print("-" * 35)

class User:
    def __init__(self, id, username, password, role):
        self.id = id  # Initialize the id attribute
        self.username = username
        self.password = password
        self.role = role
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def sign_up(cls, username, password, role):
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            print("Username already taken!")
            conn.close()
            return None

        if role == "1":
            role = "Freelancer"
            display_header("Create Your Freelancer Profile")
            name = input("Enter your name: ")
            skills = input("Enter your skills (comma separated): ")
            experience = input("Enter your experience: ")
            hourly_rate = float(input("Enter your hourly rate: "))
            payment_method = input("Enter your payment method: ")
            cursor.execute("""
                INSERT INTO users (username, password, role, name, skills, experience, hourly_rate, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (username, hashlib.sha256(password.encode()).hexdigest(), role, name, skills, experience, hourly_rate, payment_method))
        elif role == "2":
            role = "Employer"
            display_header("Create Your Employer Account")
            company_name = input("Enter your company name: ")
            cursor.execute("""
                INSERT INTO users (username, password, role, company_name)
                VALUES (?, ?, ?, ?)""",
                (username, hashlib.sha256(password.encode()).hexdigest(), role, company_name))
        else:
            print("Invalid choice!")
            conn.close()
            return None
        
        conn.commit()
        conn.close()
        print("\nSign-up successful! You can now log in.")
        time.sleep(2)
        os.system("cls")
        return cls(username, password, role)
    
    @classmethod
    def login(cls, username, password):
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and user_data[2] == hashlib.sha256(password.encode()).hexdigest():
            print(f"\nLogin successful! Welcome, {username}.")
            time.sleep(2)
            os.system("cls")
            if user_data[3] == "Freelancer":
                return Freelancer(*user_data)  # Pass all user_data to Freelancer
            else:
                return Employer(*user_data)  # Pass all user_data to Employer

        print("\nInvalid username or password!")
        time.sleep(2)
        os.system("cls")
        return None
        
    @staticmethod
    def display_all_users():
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()
        
        display_header("All Users")
        for user in users:
            print(user)
        divider()
    
    def logout(self):
        print(f"\n{self.username} has logged out.")
        time.sleep(2)
        os.system("cls")
        
class Freelancer(User):
    def __init__(self, id, username, password, role, name=None, skills=None, experience=None, hourly_rate=None, payment_method=None, company_name=None):
        super().__init__(id, username, password, role)  # Pass common attributes to the parent class
        self.name = name
        self.skills = skills.split(", ") if skills else []
        self.experience = experience
        self.hourly_rate = hourly_rate
        self.payment_method = payment_method

        
    def browse_jobs(self):
        """Fetch and display all jobs from the database."""
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        # Fetch all jobs from the database
        cursor.execute("""
            SELECT id, title, description, budget, skills_required, duration, status
            FROM jobs
            WHERE status = 'open'
        """)
        jobs = cursor.fetchall()
        conn.close()

        if not jobs:
            print("No jobs available at the moment.")
            return

        print("\nAvailable Jobs:\n" + "=" * 50)
        for job in jobs:
            job_id, title, description, budget, skills_required, duration, status = job

            print(f"[{job_id}] {title}")
            print(f"   Description: {description}")
            print(f"   Budget: ${budget}")
            print(f"   Skills Required: {skills_required}")
            print(f"   Duration: {duration}")
            print(f"   Status: {status.capitalize()}")
            print("=" * 50)

        input("\nPress Enter to return to the dashboard...")  # Wait for user input before returning

    def apply_job(self, job):
            """Apply for a job by inserting an application into the database."""
            if not isinstance(job, job_system.Job):
                raise TypeError("Job must be an instance of Job class")

            conn = sqlite3.connect("freelancer_marketplace.db")
            cursor = conn.cursor()

            # Check if the freelancer has already applied for this job
            cursor.execute("""
                SELECT * FROM job_applications WHERE job_id = ? AND freelancer_id = ?
            """, (job.id, self.id))
            existing_application = cursor.fetchone()

            if existing_application:
                print("You have already applied for this job.")
                conn.close()
                return

            # Create an application entry in the database
            cursor.execute("""
                INSERT INTO job_applications (job_id, freelancer_id, status)
                VALUES (?, ?, 'applied')
            """, (job.id, self.id))

            conn.commit()
            conn.close()

            # Add the freelancer to the job's applicant list
            job.add_applicant(self)
            print(f"Successfully applied for the job: {job.title}")
        
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

        print("\nYour Job Applications:\n" + "="*50)
        for app_id, title, budget, status in applications:
            print(f"Application ID: {app_id}")
            print(f"   Job Title: {title}")
            print(f"   Budget: ${budget}")
            print(f"   Status: {status}")
            print("="*50)
    
    
    def edit_profile(self):
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()
        display_header("Edit Profile")
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
            os.system("cls")
            return
        
        conn.commit()
        conn.close()
        print("Profile updated successfully!")

class Employer(User):
    def __init__(self, id, username, password, role, name=None, skills=None, experience=None, hourly_rate=None, payment_method=None, company_name=None):
        super().__init__(id, username, password, role)  # Pass common attributes to the parent class
        self.company_name = company_name
        self.posted_jobs = []  # List to store jobs posted by the employer

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

        conn.commit()
        conn.close()

        print(f"Job '{title}' has been successfully posted with ID {job_id}.")

        return job  # Returning the job instance

        
    def view_applicants(self, job):
        """Displays applicants for a specific job posted by the employer."""
        if job in self.posted_jobs:
            return job.applicants
        else:
            raise ValueError("This job was not posted by this employer.")
    
    def accept_proposal(self, job, freelancer):
        """Accepts a freelancer's application for a job."""
        if job in self.posted_jobs and freelancer in job.applicants:
            return f"{freelancer.name} has been accepted for {job.title}"
        else:
            raise ValueError("Invalid job or freelancer.")
    
    def reject_proposal(self, job, freelancer):
        """Rejects a freelancer's application for a job."""
        if job in self.posted_jobs and freelancer in job.applicants:
            job.applicants.remove(freelancer)
            return f"{freelancer.name} has been rejected for {job.title}"
        else:
            raise ValueError("Invalid job or freelancer.")

def freelancer_menu(user):
    """Handles freelancer actions like browsing jobs and tracking applications."""
    while True:
        os.system("cls")  # Clear the terminal only once at the start of the loop
        print("\n--- Freelancer Dashboard ---")
        print("[1] Browse Jobs\n[2] Apply for Job\n[3] Track Applications\n[4] Logout")
        choice = input("Select an option: ")

        if choice == "1":
            user.browse_jobs()  # Display jobs without clearing the terminal again
        elif choice == "2":
            job_id = input("Enter Job ID to apply: ")
            user.apply_for_job(job_id)
        elif choice == "3":
            user.track_applications()
        elif choice == "4":
            print("Logging out...")
            time.sleep(2)
            break  # Exit the freelancer dashboard
        else:
            print("Invalid choice! Please try again.")
            time.sleep(2)

def employer_menu(user):
    """Handles employer actions like posting jobs and managing applications."""
    while True:
        os.system("cls")
        print("\n--- Employer Dashboard ---")
        print("[1] Post a Job\n[2] View Applicants\n[3] Manage Payments\n[4] Logout")
        choice = input("Select an option: ")

        if choice == "1":
            # Collect all required job details
            title = input("Enter Job Title: ")
            description = input("Enter Job Description: ")
            budget = float(input("Enter Budget: "))
            skill_required = input("Enter Skills Required (comma-separated): ")
            duration = input("Enter Job Duration (e.g., 1 month): ")

            # Call the post_job method with all required arguments
            user.post_job(title, description, budget, skill_required, duration)
            print("Job posted successfully!")
            time.sleep(2)

        elif choice == "2":
            job_id = input("Enter Job ID to view applicants: ")
            Employer.view_applicants(job_id)

        elif choice == "3":
            manage_payments(user)

        elif choice == "4":
            print("Logging out...")
            break  # Exit the Employer dashboard and return to the main menu
        else:
            print("Invalid choice! Please try again.")
            time.sleep(2)


def manage_payments(user):
    """Handles employer payments, milestones, and approvals."""
    while True:
        os.system("cls")
        print("\n--- Payment Management ---")
        print("[1] Deposit Funds\n[2] Set Milestones\n[3] Approve Work & Release Payment\n[4] Back")
        choice = input("Select an option: ")

        if choice == "1":
            job_id = input("Enter Job ID to deposit funds: ")
            amount = input("Enter deposit amount: ")
            user.deposit_funds(job_id, amount)

        elif choice == "2":
            job_id = input("Enter Job ID to set milestones: ")
            milestones = input("Enter milestones (comma-separated): ")
            user.set_milestones(job_id, milestones)

        elif choice == "3":
            job_id = input("Enter Job ID to approve work: ")
            user.approve_work_and_release_payment(job_id)

        elif choice == "4":
            break

def main():
    init_db()  # Initialize the database
    while True:
        display_header("Welcome to ProDigi")
        print("[1] Sign Up\n[2] Login\n[3] Display Users\n[4] Exit\n[5] Database Checker")
        divider()
        choice = input("Select an option: ")

        if choice == "1":
            # Sign Up
            username = input("Enter username: ")
            password = input("Enter password: ")
            os.system("cls")
            display_header("Select Your Role")
            print("[1] Freelancer\n[2] Employer")
            divider()
            role = input("Enter role: ")
            User.sign_up(username, password, role)

        elif choice == "2":
            # Login
            username = input("Enter username: ")
            password = input("Enter password: ")
            user = User.login(username, password)

            if user:
                os.system("cls")
                print(f"Welcome, {user.username}! Logged in successfully.")
                time.sleep(2)
                os.system("cls")

                # Stay in the dashboard until the user logs out
                while True:
                    if user.role == "Freelancer":
                        freelancer_menu(user)  # Enter Freelancer dashboard
                    elif user.role == "Employer":
                        employer_menu(user)  # Enter Employer dashboard
                    else:
                        print("Invalid role! Returning to main menu.")
                        break  # Exit the dashboard loop and return to the main menu

                    # If the user logs out, break the dashboard loop
                    break

        elif choice == "3":
            # Display All Users
            User.display_all_users()

        elif choice == "4":
            # Exit
            print("Exiting... Goodbye!")
            break
        elif choice == "5":
            # Database checker
            display_jobs_table()
            break
        
        else:
            print("Invalid choice! Please try again.")
            time.sleep(2)
            os.system("cls")

if __name__ == "__main__":
    main()

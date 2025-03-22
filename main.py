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
            print("\nAvailable Jobs:\n" + "=" * 50)
            for job in jobs:
                job_id, title, description, budget, skills_required, duration = job
                print(f"[{job_id}] {title}")
                print(f"   Description: {description}")
                print(f"   Budget: ${budget}")
                print(f"   Skills Required: {skills_required}")
                print(f"   Duration: {duration}")
                print("=" * 50)

            # Provide freelancer options
            print("\nOptions:")
            print("1. Search Job")
            print("2. Apply Job")
            print("3. Exit to Dashboard")

            choice = input("Enter your choice (1/2/3): ").strip()

            if choice == "1":
                self.search_job()
            elif choice == "2":
                self.apply_job()
            elif choice == "3":
                print("Returning to freelancer dashboard...")
                break  # Exits the loop and returns to the freelancer dashboard
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

    # Function to search for a job by title
    def search_job(self):
        """Search for jobs based on the job title."""
        
        job_title = input("Enter the job title to search: ").strip()

        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, description, budget, skills_required, duration
            FROM jobs
            WHERE title LIKE ?
        """, ('%' + job_title + '%',))
        
        jobs = cursor.fetchall()
        conn.close()

        if not jobs:
            print("No jobs found matching your search.")
        else:
            os.system("cls")
            print("\nSearch Results:\n" + "=" * 50)
            for job in jobs:
                job_id, title, description, budget, skills_required, duration = job
                print(f"[{job_id}] {title}")
                print(f"   Description: {description}")
                print(f"   Budget: ${budget}")
                print(f"   Skills Required: {skills_required}")
                print(f"   Duration: {duration}")
                print("=" * 50)

        input("Press Enter to return to the Browse Jobs menu...")  # Prevents instant return

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
            print("Job not found. Please check the title and try again.")
        else:
            job_id = job[0]

            # Insert application into the database
            cursor.execute("""
                INSERT INTO job_applications (job_id, freelancer_id, status)
                VALUES (?, ?, 'applied')
            """, (job_id, self.id))

            conn.commit()
            print(f"Your application for '{job_title}' has been submitted successfully!")

        conn.close()
        input("Press Enter to return to the Browse Jobs menu...")  # Prevents instant return
        
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
        
        input("Press Enter to return to the Browse Jobs menu...")
    
    
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
        job.id = job_id  # Assign the ID to the job object

        conn.commit()
        conn.close()

        # Add job to employer's posted jobs list
        self.posted_jobs.append(job)

        print(f"Job '{title}' has been successfully posted with ID {job_id}.")
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

        # Display applicants
        print(f"\nApplicants for '{job_title}':\n" + "=" * 50)
        for freelancer_id, name, skills, experience, hourly_rate, application_id in applicants:
            print(f"[{name}]")  # <-- Freelancer Name instead of ID
            print(f"  Skills: {skills}")
            print(f"  Experience: {experience}")
            print(f"  Hourly Rate: ${hourly_rate:.2f}/hr")
            print("=" * 50)

        # Manage applicants
        while True:
            action = input("\nEnter Freelancer Name to manage application or 'exit' to return: ").strip()

            if action.lower() == "exit":
                break

            applicant = next((app for app in applicants if app[1].lower() == action.lower()), None)

            if not applicant:
                print("Invalid Freelancer Name. Try again.")
                continue

            _, name, skills, experience, hourly_rate, application_id = applicant
            self.manage_applicant(application_id, name, skills, experience, hourly_rate)

    def manage_applicant(self, application_id, name, skills, experience, hourly_rate):
        """Allows the employer to view the applicant profile and accept/reject them."""

        print(f"\n[Profile - {name}]")
        print(f"  Skills: {skills}")
        print(f"  Experience: {experience}")
        print(f"  Hourly Rate: ${hourly_rate:.2f}/hr")

        # Accept or Reject
        while True:
            decision = input("\nAccept (A) or Reject (R) this applicant? ").strip().lower()
            if decision in ["a", "r"]:
                new_status = "accepted" if decision == "a" else "rejected"
                print(f"{name} has been {'accepted' if decision == 'a' else 'rejected'}.")

                # Update database
                conn = sqlite3.connect("freelancer_marketplace.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE job_applications SET status = ? WHERE id = ?", (new_status, application_id))
                conn.commit()
                conn.close()
                break
            else:
                print("Invalid input. Please enter 'A' to accept or 'R' to reject.")
        
    def print_posted_jobs(self):
        """Fetch and print all jobs posted by the employer."""
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, description, budget, skills_required, duration, status
            FROM jobs
            WHERE employer_id = ?
        """, (self.id,))

        jobs = cursor.fetchall()
        conn.close()

        if not jobs:
            print("You have not posted any jobs yet.")
            return

        print("\n--- Your Posted Jobs ---")
        for job in jobs:
            job_id, title, description, budget, skills, duration, status = job
            print(f"\nJob ID: {job_id}\nTitle: {title}\nDescription: {description}\nBudget: ${budget}\nSkills Required: {skills}\nDuration: {duration}\nStatus: {status}")
            print("-" * 50)

def freelancer_menu(user):
    """Handles freelancer actions like browsing jobs and tracking applications."""
    while True:
        os.system("cls")  # Clear the terminal only once at the start of the loop
        print("\n--- Freelancer Dashboard ---")
        print("[1] Browse Jobs\n[2] Apply for Job\n[3] Track Applications\n[4] Logout")
        choice = input("Select an option: ")

        if choice == "1":
            user.browse_jobs()  # Display jobs without clearing the terminal again
        #elif choice == "2":
           # job_id = input("Enter Job ID to apply: ")
            #user.apply_job(job_id)
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
        os.system("cls")  # Clear the terminal
        print("\n--- Employer Dashboard ---")
        print("[1] Post a Job\n[2] View Applicants\n[3] Manage Payments\n[4] View Posted Jobs\n[5] Logout")
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
            try:
                job_title = input("Enter Job ID to view applicants: ") # Convert to int
                user.view_applicants(job_title)
                input("\nPress Enter to return to the dashboard...")  # Pause before clearing screen
            except ValueError:
                print("Invalid input! Job ID must be a number.")
                time.sleep(2)

        elif choice == "3":
            manage_payments(user)

        elif choice == "4":
            user.print_posted_jobs()  # Correct way to call the method
            input("\nPress Enter to return to the dashboard...")  # Pause before clearing screen

        elif choice == "5":
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
        print("[1] Sign Up\n[2] Login\n[3] Exit")
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
            # Exit
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice! Please try again.")
            time.sleep(2)
            os.system("cls")

if __name__ == "__main__":
    main()

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

def display_menu(title=None, options=[]):
    if title:  # Only display header if title is provided
        display_header(title)
    
    for i, option in enumerate(options, 1):
        print(f"[{i}] {option}")
    divider()
    return input("Select an option: ")


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
            print("\nUsername already taken!")
            time.sleep(1.5)
            os.system("cls")
            conn.close()
            return None

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if role == "1":
            role = "Freelancer"
            os.system("cls")
            display_header("Create Your Freelancer Profile")
            name = input("Enter your name: ")
            skills = input("Enter your skills (comma separated): ")
            experience = input("Enter your experience: ")
            hourly_rate = float(input("Enter your hourly rate: "))
            payment_method = input("Enter your payment method: ")

            cursor.execute("""
                INSERT INTO users (username, password, role, name, skills, experience, hourly_rate, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (username, hashed_password, role, name, skills, experience, hourly_rate, payment_method))
        elif role == "2":
            role = "Employer"
            os.system("cls")
            display_header("Create Your Employer Account")
            company_name = input("Enter your company name: ")

            cursor.execute("""
                INSERT INTO users (username, password, role, company_name)
                VALUES (?, ?, ?, ?)""",
                (username, hashed_password, role, company_name))
        else:
            print("Invalid choice!")
            conn.close()
            return None

        # Get the last inserted ID
        user_id = cursor.lastrowid  

        conn.commit()
        conn.close()

        print("\nSign-up successful! You can now log in.")
        time.sleep(2)
        os.system("cls")

        # Return the new User instance with all required arguments
        return cls(user_id, username, hashed_password, role)  

   
    @classmethod
    def login(cls, username, password):
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and user_data[2] == hashlib.sha256(password.encode()).hexdigest():
            print(f"\nLogin successful! Welcome, {username}.")
            time.sleep(2)
            os.system("cls")

            # Extract only the necessary values
            user_id, username, password, role = user_data

            if role == "Freelancer":
                return Freelancer(user_id, username, password, role)  # Pass only the expected values
            else:
                return Employer(user_id, username, password, role)  # Pass only the expected values

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
            os.system("cls")
            display_header("Available Jobs")
            for index, job in enumerate(jobs):
                job_id, title, description, budget, skills_required, duration = job
                print(f"[{job_id}] Title: {title}")
                print(f"    Description: {description}")
                print(f"    Budget: ${budget}")
                print(f"    Skills Required: {skills_required}")
                print(f"    Duration: {duration}")

                # Only print divider if it's not the last job
                if index < len(jobs) - 1:
                    divider()

            choice = display_menu("Menu", ["Search Job", "Apply Job", "Exit to Dashboard"])

            if choice == "1":
                self.search_job()
            elif choice == "2":
                self.apply_job()
            elif choice == "3":
                print("Returning to freelancer dashboard...")
                break  # Exits the loop and returns to the freelancer dashboard
            else:
                print("\nInvalid choice. Please try again!")
                time.sleep(1.5)

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

        os.system("cls")
        display_header("Search Results")
        
        if not jobs:
            print("No jobs found matching your search.")
            divider()
        else:
            for job in jobs:
                job_id, title, description, budget, skills_required, duration = job
                print(f"[{job_id}] Title: {title}")
                print(f"    Description: {description}")
                print(f"    Budget: ${budget}")
                print(f"    Skills Required: {skills_required}")
                print(f"    Duration: {duration}")
                divider()

        input("Press Enter to Return...")  # Prevents instant return

    # Function to apply for a job
    def apply_job(self):
        """Apply for a job based on the job title."""
        job_title = input("Enter the job title you want to apply for: ").strip()

        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()

        # Find the job ID based on the title
        cursor.execute("SELECT id FROM jobs WHERE title LIKE ?", ('%' + job_title + '%',))
        job = cursor.fetchone()

        os.system("cls")
        display_header("Apply Job")

        if not job:
            print("Job not found. Please try again.")
            divider()
        else:
            job_id = job[0]

            # Insert application into the database
            cursor.execute("""
                INSERT INTO job_applications (job_id, freelancer_id, status)
                VALUES (?, ?, 'applied')
            """, (job_id, self.id))

            conn.commit()
            print(f"Applied for '{job_title}' successfully!")
            divider()

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

        os.system("cls")
        display_header("Job Applications")
        for app_id, title, budget, status in applications:
            print(f"Application ID: {app_id}")
            print(f"Job Title: {title}")
            print(f"Budget: ${budget}")
            print(f"Status: {status}")
            divider()
       
        input("Press Enter to Return...")
   
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
            os.system("cls")
            display_header(f"Applicants for {job_title}")
            for freelancer_id, name, skills, experience, hourly_rate, application_id in applicants:
                print(f"  Applicant: {name}")  # <-- Freelancer Name instead of ID
                print(f"  Skills: {skills}")
                print(f"  Experience: {experience}")
                print(f"  Hourly Rate: ${hourly_rate:.2f}/hr")
                divider()
            action = input("Enter Applicant Name or type 'exit': ").strip()

            if action.lower() == "exit":
                break

            applicant = next((app for app in applicants if app[1].lower() == action.lower()), None)

            if not applicant:
                print("\nInvalid Freelancer Name. Try again.")
                time.sleep(1.5)
                continue

            _, name, skills, experience, hourly_rate, application_id = applicant
            self.manage_applicant(application_id, name, skills, experience, hourly_rate)

    def manage_applicant(self, application_id, name, skills, experience, hourly_rate):
        """Allows the employer to view the applicant profile and accept/reject them."""

        os.system("cls")
        display_header(f"{name}'s Profile")
        print(f"  Skills: {skills}")
        print(f"  Experience: {experience}")
        print(f"  Hourly Rate: ${hourly_rate:.2f}/hr")
        divider()

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
                conn.commit()
                conn.close()
                break
            else:
                print("Invalid input. Please enter 'A' to accept or 'R' to reject.\n")
       
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

        os.system("cls")
        display_header("Your Posted Jobs")
        for job in jobs:
            job_id, title, description, budget, skills, duration, status = job
            print(f"Job ID: {job_id}\nTitle: {title}\nDescription: {description}\nBudget: ${budget}\nSkills Required: {skills}\nDuration: {duration}\nStatus: {status}")
            divider()


def freelancer_menu(user):
    """Handles freelancer actions like browsing jobs and tracking applications."""
    while True:
        os.system("cls")  # Clear the terminal only once at the start of the loop
        choice = display_menu(f"{user.role} Menu", ["Browse and Apply Jobs", "Track Applications", "Logout"])

        if choice == "1":
            user.browse_jobs()  # Display jobs without clearing the terminal again
        elif choice == "2":
            user.track_applications()
        elif choice == "3":
            print("Logging out...")
            time.sleep(2)
            break  # Exit the freelancer dashboard
        else:
            print("Invalid choice! Please try again.")
            time.sleep(1.5)


def employer_menu(user):
    """Handles employer actions like posting jobs and managing applications."""
    while True:
        os.system("cls")  # Clear the terminal
        choice = display_menu(f"{user.role} Menu", ["Post a Job", "View Applicants", "Manage Payments", "View Posted Jobs", "Logout"])

        if choice == "1":
            # Collect all required job details
            os.system("cls")
            display_header("Post Job")
            title = input("Enter Job Title: ")
            description = input("Enter Job Description: ")
            budget = float(input("Enter Budget: "))
            skill_required = input("Enter Skills Required (comma-separated): ")
            duration = input("Enter Job Duration (e.g., 1 month): ")
            # Call the post_job method with all required arguments
            user.post_job(title, description, budget, skill_required, duration)
            print("\nJob posted successfully!")
            time.sleep(2)
        elif choice == "2":
            try:
                job_title = input("Enter Job ID to view applicants: ") # Convert to int
                user.view_applicants(job_title)
                input("\nPress Enter to Return...")  # Pause before clearing screen
            except ValueError:
                print("Invalid input! Job ID must be a number.")
                time.sleep(2)
        elif choice == "3":
            manage_payments(user)
        elif choice == "4":
            user.print_posted_jobs()  # Correct way to call the method
            input("Press Enter to Return...")  # Pause before clearing screen
        elif choice == "5":
            print("Logging out...")
            time.sleep(2)
            break  # Exit the Employer dashboard and return to the main menu
        else:
            print("Invalid choice! Please try again.")
            time.sleep(1.5)

def manage_payments(user):
    """Handles employer payments, milestones, and approvals."""
    while True:
        os.system("cls")
        display_header("Payment Management")
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

def display_sign_up():
    os.system("cls")
    display_header("Sign Up")
    username = input("Enter username: ")
    password = input("Enter password: ")

    os.system("cls")
    display_header("Select Your Role")
    print("[1] Freelancer - Find and apply for jobs\n[2] Employer - Post jobs and hire talent ")
    divider()
    role = input("Enter role: ")
    User.sign_up(username, password, role)

def display_login():
    os.system("cls")
    display_header("Login")
    username = input("Enter username: ")
    password = input("Enter password: ")
    return User.login(username, password)

def main():
    init_db()  # Initialize the database
    while True:
        os.system("cls")
        display_header("Welcome to ProDigi")
        print("[1] Sign Up\n[2] Login\n[3] Exit")
        divider()
        choice = input("Select an option: ")

        if choice == "1":
            display_sign_up()
        elif choice == "2":
            user = display_login()
            if user:
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
            print("\nInvalid choice! Please try again.")
            time.sleep(1.5)
            os.system("cls")


if __name__ == "__main__":
    main()

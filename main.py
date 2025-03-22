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
        os.system("cls")
        if any(user.username == username for user in cls.users):
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
        pass
    
    def apply_job(self):
        pass
    
    def track_applications(self):
        pass
    
    def edit_profile(self):
        while True:
            os.system("cls")
            display_header("Edit Profile")
            print(f"[1] Name: {self.name}\n[2] Skills: {', '.join(self.skills)}\n[3] Experience: {self.experience}\n[4] Hourly Rate: ${self.hourly_rate}\n[5] Payment Method: {self.payment_method}")
            divider()
            choice = input("Select field to edit [1-5] or [6] Back: ")
            
            if choice == "1":
                self.name = input("Enter new name: ")
            elif choice == "2":
                self.skills = input("Enter new skills (comma separated): ").split(',')
            elif choice == "3":
                self.experience = input("Enter new experience: ")
            elif choice == "4":
                self.hourly_rate = float(input("Enter new hourly rate: "))
            elif choice == "5":
                self.payment_method = input("Enter new payment method: ")
            elif choice == "6":
                os.system("cls")
                break
            else:
                print("Invalid choice!")
                continue
            
            User.save_users()
            print("Profile updated successfully!")

class Employer(User):
    def __init__(self, id, username, password, role, name=None, skills=None, experience=None, hourly_rate=None, payment_method=None, company_name=None):
        super().__init__(id, username, password, role)  # Pass common attributes to the parent class
        self.company_name = company_name
    
    def post_job(self):
        pass
    
    def view_applicants(self):
        pass
    
    def accept_proposal(self):
        pass
    
    def reject_proposal(self):
        pass

User.load_users()

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
        display_header(f"{user.role} Menu")
        
        if isinstance(user, Freelancer):
            options = [
                "[1] Browse Jobs", 
                "[2] Apply Jobs", 
                "[3] Track Applications", 
                "[4] Edit Profile", 
                "[5] Logout"
            ]
        elif isinstance(user, Employer):
            options = [
                "[1] Post Job", 
                "[2] View Applicants", 
                "[3] Accept Proposal", 
                "[4] Reject Proposal", 
                "[5] Logout"
            ]
        
        print("\n".join(options))
        divider()
        
        sub_choice = input("Select an option: ")
        
        if isinstance(user, Freelancer) and sub_choice == "4":
            user.edit_profile()
        if sub_choice == "5":
            user.logout()
            break

def main():
    init_db()  # Initialize the database
    while True:
        display_header("Welcome to ProDigi")
        print("[1] Sign Up\n[2] Login\n[3] Exit")
        divider()
        choice = input("Select an option: ")

        if choice == "1":
            display_sign_up()
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

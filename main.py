import sqlite3
import hashlib
import os
import time
from user import User
from utils import Utility
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


def freelancer_menu(user):
    """Handles freelancer actions like browsing jobs and tracking applications."""
    while True:
        Utility.clear_screen()  # Clear the terminal only once at the start of the loop
        choice = Utility.display_menu(f"{user.role} Menu", ["Browse and Apply Jobs", "Track Applications", "Edit Profile", "Logout"])

        if choice == "1":
            user.browse_jobs()  # Display jobs without clearing the terminal again
        elif choice == "2":
            user.track_applications()
        elif choice == "3":
            user.edit_profile()
        elif choice == "4":
            print("Logging out...")
            time.sleep(2)
            break  # Exit the freelancer dashboard
        else:
            print("Invalid choice! Please try again.")
            time.sleep(1.5)


def employer_menu(user):
    """Handles employer actions like posting jobs and managing applications."""
    while True:
        Utility.clear_screen()  # Clear the terminal
        choice = Utility.display_menu(f"{user.role} Menu", ["Post a Job", "View Applicants", "Manage Payments", "View Posted Jobs", "Logout"])

        if choice == "1":
            # Collect all required job details
            Utility.clear_screen()
            Utility.display_header("Post Job")
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
        Utility.clear_screen()
        Utility.display_header("Payment Management")
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
    Utility.clear_screen()
    Utility.display_header("Sign Up")
    username = input("Enter username: ")
    password = input("Enter password: ")

    Utility.clear_screen()
    Utility.display_header("Select Your Role")
    print("[1] Freelancer - Find and apply for jobs\n[2] Employer - Post jobs and hire talent ")
    Utility.divider()
    role = input("Enter role: ")
    User.sign_up(username, password, role)

def display_login():
    Utility.clear_screen()
    Utility.display_header("Login")
    username = input("Enter username: ")
    password = input("Enter password: ")
    return User.login(username, password)

def main():
    init_db()  # Initialize the database
    while True:
        Utility.clear_screen()
        Utility.display_header("Welcome to ProDigi")
        print("[1] Sign Up\n[2] Login\n[3] Exit")
        Utility.divider()
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
            Utility.clear_screen()

if __name__ == "__main__":
    main()
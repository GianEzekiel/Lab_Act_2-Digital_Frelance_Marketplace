import sqlite3
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
        choice = Utility.display_menu(f"{user.role} Menu", ["Browse and Apply Jobs", "Track Applications", "Work in Progress", "Wallet & Payment","Edit Profile", "Logout"])

        if choice == "1":
            user.browse_jobs()  # Display jobs without clearing the terminal again
        elif choice == "2":
            user.track_applications()
        elif choice == "3":
            job_id = select_job(user)
            if job_id:
                progress_display(user, job_id)
        elif choice == "4":
            user.wallet_menu()
        elif choice == "5":
            user.edit_profile()
        elif choice == "6":
            user.logout()
            break  # Exit the freelancer dashboard
        else:
            print("Invalid choice! Please try again.")
            time.sleep(1.5)


def employer_menu(user):
    """Handles employer actions like posting jobs and managing applications."""
    while True:
        Utility.clear_screen()  # Clear the terminal
        choice = Utility.display_menu(f"{user.role} Menu", ["Post a Job", "View Applicants", "Work in Progress","Wallet & Payment Settings", "View Posted Jobs", "Logout"])

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
            job_id = select_job(user)  # Ensures the employer selects a job first
            if job_id:
                progress_display(user, job_id)  # Pass selected job_id
            input("\nPress Enter to return to the dashboard...")
        elif choice == "4":
            user.wallet_menu()  # New function for wallet & payment
        elif choice == "5":
            user.view_posted_jobs()  # Correct way to call the method
            input("Press Enter to Return...")  # Pause before clearing screen
        elif choice == "6":
            user.logout()
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

def select_job(user):
    """Prompts the user to select a job before accessing Work in Progress."""

    conn = sqlite3.connect("freelancer_marketplace.db")
    cursor = conn.cursor()

    if user.role == "Freelancer":
        cursor.execute('''
            SELECT j.id, j.title
            FROM jobs j
            JOIN job_applications ja ON j.id = ja.job_id
            WHERE ja.freelancer_id = ? AND j.status = 'in_progress'
        ''', (user.id,))
    else:  # Employer
        cursor.execute('''
            SELECT id, title
            FROM jobs
            WHERE employer_id = ? AND status IN ('in_progress', 'completed')
        ''', (user.id,))

    jobs = cursor.fetchall()
    conn.close()

    if not jobs:
        print("No active jobs found.")
        return None

    print("\nSelect a job:")
    for idx, (job_id, title) in enumerate(jobs, 1):
        print(f"[{idx}] {title}")

    try:
        job_choice = int(input("Enter job number: ")) - 1
        if job_choice < 0 or job_choice >= len(jobs):
            print("Invalid choice.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None

    selected_job_id, selected_title = jobs[job_choice]
    print(f"\nSelected Job: {selected_title}\n")

    return selected_job_id  # Return job_id to pass into progress_display

def progress_display(user, job_id):
    """Displays work in progress for both freelancers and employers."""

    Utility.display_header("Work in Progress")

    conn = sqlite3.connect("freelancer_marketplace.db")
    cursor = conn.cursor()

    # Get job details
    cursor.execute("SELECT title, description, status FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()

    if not job:
        print("Error: Job not found.")
        conn.close()
        return

    job_title, job_description, job_status = job

    if job_status != "in_progress":
        print("This job is not currently in progress.")
        conn.close()
        return

    print(f"\nJob: {job_title}\nDescription: {job_description}\n")

    # Fetch milestones based on the user role
    if user.role == "freelancer":
        cursor.execute('''
            SELECT id, title, payment, status
            FROM milestones
            WHERE job_id = ? AND freelancer_id = ?
        ''', (job_id, user.id))
    else:  # Employer
        cursor.execute('''
            SELECT id, title, payment, status
            FROM milestones
            WHERE job_id = ?
        ''', (job_id,))

    milestones = cursor.fetchall()

    if not milestones:
        print("No milestones found for this job.")
    else:
        print("\nMilestones:")
        for idx, (milestone_id, title, payment, status) in enumerate(milestones, 1):
            print(f"[{idx}] {title} (Php {payment}) [{status}]")

    conn.close()

    # Options for freelancers
    if user.role == "Freelancer":
        while True:
            print("\nOptions:")
            print("1. Submit Milestone")
            print("2. Go Back")


            choice = input("Enter choice: ").strip()


            if choice == "1":
                milestone_title = input("Enter milestone title to submit: ").strip()
                user.submit_milestone(milestone_title)  # Now submits by title
            elif choice == "2":
                break
            else:
                print("Invalid choice. Please select a valid option.")


    # Options for employers
    elif user.role == "Employer":
        while True:
            print("\nOptions:")
            print("1. Add Milestone")
            print("2. Approve Milestone")
            print("3. Go Back")


            choice = input("Enter choice: ").strip()


            if choice == "1":
                user.add_milestone(job_id)
            elif choice == "2":
                milestone_title = input("Enter milestone title to submit: ").strip()
                user.approve_milestone(milestone_title)
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please select a valid option.")


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
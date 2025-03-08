import hashlib
import json
import os
import time

class User:
    users = []  # Store all registered users
    FILE_PATH = "users.json"
    
    def __init__(self, username, password, role):
        self.username = username
        self.password = self.hash_password(password)
        self.role = role
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    @classmethod
    def save_users(cls):
        with open(cls.FILE_PATH, "w") as file:
            json.dump([user.__dict__ for user in cls.users], file)
    
    @classmethod
    def load_users(cls):
        try:
            with open(cls.FILE_PATH, "r") as file:
                data = json.load(file)
                for user in data:
                    if user["role"] == "Freelancer":
                        new_user = Freelancer(user["username"], user["password"], user["name"], user["skills"], user["experience"], user["hourly_rate"], user["payment_method"])
                    elif user["role"] == "Employer":
                        new_user = Employer(user["username"], user["password"], user["company_name"])
                    else:
                        continue
                    new_user.password = user["password"]  # Keep hashed password
                    cls.users.append(new_user)
        except (FileNotFoundError, json.JSONDecodeError):
            cls.users = []
    
    @classmethod
    def sign_up(cls, username, password, role):
        os.system("cls")
        if any(user.username == username for user in cls.users):
            print("Username already taken!")
            return None
        
        if role == "1":
            role = "Freelancer"
            print("=================================")
            print("  Create Your Freelancer Profile ")
            print("=================================")
            name = input("Enter your name: ")
            skills = input("Enter your skills (comma separated): ").split(',')
            experience = input("Enter your experience: ")
            hourly_rate = float(input("Enter your hourly rate: "))
            payment_method = input("Enter your payment method: ")
            new_user = Freelancer(username, password, name, skills, experience, hourly_rate, payment_method)
        elif role == "2":
            role = "Employer"
            print("=================================")
            print("   Create Your Employer Account  ")
            print("=================================")
            company_name = input("Enter your company name: ")
            new_user = Employer(username, password, company_name)
        else:
            print("Invalid choice!")
            return None
        
        cls.users.append(new_user)
        cls.save_users()
        print("\nSign-up successful! You can now log in.")
        time.sleep(2)
        os.system("cls")
        return new_user
    
    @classmethod
    def login(cls, username, password):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        for user in cls.users:
            if user.username == username and user.password == hashed_pw:
                print(f"\nLogin successful! Welcome, {username}.")
                time.sleep(2)
                os.system("cls")
                return user
        print("\nInvalid username or password!")
        time.sleep(2)
        os.system("cls")
        return None
    
    def logout(self):
        print(f"\n{self.username} has logged out.")
        time.sleep(2)
        os.system("cls")
        return None

class Freelancer(User):
    def __init__(self, username, password, name, skills, experience, hourly_rate, payment_method):
        super().__init__(username, password, "Freelancer")
        self.name = name
        self.skills = skills
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
            print("=========================================")
            print("               Edit Profile              ")
            print("=========================================")
            print(f"[1] Name: {self.name}\n[2] Skills: {', '.join(self.skills)}\n[3] Experience: {self.experience}\n[4] Hourly Rate: ${self.hourly_rate}\n[5] Payment Method: {self.payment_method}")
            print("-----------------------------------------")
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
    def __init__(self, username, password, company_name):
        super().__init__(username, password, "Employer")
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
    print("=================================")
    print("             Sign Up             ")
    print("=================================")
    username = input("Enter username: ")
    password = input("Enter password: ")

    os.system("cls")
    print("=========================================")
    print("             Select Your Role            ")
    print("=========================================")
    print("[1] Freelancer - Find and apply for jobs\n[2] Employer - Post jobs and hire talent ")
    print("-----------------------------------------")
    role = input("Enter role: ")
    User.sign_up(username, password, role)

def display_login():
    os.system("cls")
    print("=================================")
    print("              Login              ")
    print("=================================")
    username = input("Enter username: ")
    password = input("Enter password: ")
    return User.login(username, password)

def display_menu(user):
    while True:
        os.system("cls")
        print("=================================")
        print(f"         {user.role} Menu        ")
        print("=================================")
        
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
        print("---------------------------------")
        
        sub_choice = input("Select an option: ")
        
        if isinstance(user, Freelancer) and sub_choice == "4":
            user.edit_profile()
        if sub_choice == "5":
            user.logout()
            break

def main():
    while True:
        print("=================================")
        print("         Welcome to MyApp        ")
        print("=================================")
        print("[1] Sign Up\n[2] Login\n[3] Exit")
        print("---------------------------------")
        choice = input("Select an option: ")
        
        if choice == "1":
            display_sign_up()
        elif choice == "2":
            user = display_login()
            if user:
                display_menu(user)
        elif choice == "3":
            print("Exiting... Goodbye!")
            break

if __name__ == "__main__":
    main()

import hashlib
import json
import os

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
        
        if role == "Freelancer":
            print("=================================")
            print("  Create Your Freelancer Profile ")
            print("=================================")
            name = input("Enter your name: ")
            skills = input("Enter your skills (comma separated): ").split(',')
            experience = input("Enter your experience: ")
            hourly_rate = float(input("Enter your hourly rate: "))
            payment_method = input("Enter your payment method: ")
            new_user = Freelancer(username, password, name, skills, experience, hourly_rate, payment_method)
        elif role == "Employer":
            print("=================================")
            print("   Create Your Employer Account  ")
            print("=================================")
            company_name = input("Enter your company name: ")
            new_user = Employer(username, password, company_name)
        else:
            print("Invalid role!")
            return None
        
        cls.users.append(new_user)
        cls.save_users()
        print("Sign-up successful! You can now log in.")
        return new_user
    
    @classmethod
    def login(cls, username, password):
        os.system("cls")
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        for user in cls.users:
            if user.username == username and user.password == hashed_pw:
                print(f"Login successful! Welcome, {username}.")
                return user
        print("Invalid username or password!")
        return None
    
    def logout(self):
        print(f"{self.username} has logged out.")
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
    
    def view_profile(self):
        while True:
            os.system("cls")
            print("=================================")
            print("        Freelancer Profile        ")
            print("=================================")
            print(f"Name: {self.name}\nSkills: {', '.join(self.skills)}\nExperience: {self.experience}\nHourly Rate: ${self.hourly_rate}\nPayment Method: {self.payment_method}")
            print("\n[1] Back")
            choice = input("Select an option: ")
            if choice == "1":
                os.system("cls")
                break
    
    def edit_profile(self):
        while True:
            os.system("cls")
            print("=================================")
            print("        Edit Profile        ")
            print("=================================")
            print("\nWhich field would you like to edit?")
            print("[1] Name\n[2] Skills\n[3] Experience\n[4] Hourly Rate\n[5] Payment Method\n[6] Back")
            choice = input("Enter the number of the field to edit: ")
            
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

def main():
    while True:
        print("=================================")
        print("         Welcome to MyApp        ")
        print("=================================")
        print("[1] Sign Up\n[2] Login\n[3] Exit")
        print("---------------------------------")
        choice = input("Select an option: ")
        
        if choice == "1":
            os.system("cls")
            print("=================================")
            print("             Sign Up             ")
            print("=================================")
            username = input("Enter username: ")
            password = input("Enter password: ")
            role = input("Enter role (Freelancer/Employer): ")
            User.sign_up(username, password, role)
        
        elif choice == "2":
            os.system("cls")
            print("=================================")
            print("              Login              ")
            print("=================================")
            username = input("Enter username: ")
            password = input("Enter password: ")
            user = User.login(username, password)
            
            if user:
                while True:
                    os.system("cls")
                    if isinstance(user, Freelancer):
                        print("=================================")
                        print("          Freelancer Menu        ")
                        print("=================================")
                        print("[1] Browse Jobs\n[2] Apply Jobs\n[3] Track Applications\n[4] View Profile\n[5] Edit Profile\n[6] Logout")
                    elif isinstance(user, Employer):
                        print("=================================")
                        print("           Employer Menu         ")
                        print("=================================")
                        print("[1] Post Job\n[2] View Applicants\n[3] Accept Proposal\n[4] Reject Proposal\n[5] Logout")
                    
                    print("---------------------------------")
                    sub_choice = input("Select an option: ")
                    
                    if sub_choice == "4" and isinstance(user, Freelancer):
                        user.view_profile()
                    elif sub_choice == "5" and isinstance(user, Freelancer):
                        user.edit_profile()
                    elif sub_choice == "6" or (sub_choice == "5" and isinstance(user, Employer)):
                        user.logout()
                        break
        elif choice == "3":
            print("Exiting... Goodbye!")
            break

if __name__ == "__main__":
    main()

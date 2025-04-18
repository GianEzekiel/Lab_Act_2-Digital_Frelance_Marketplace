import sqlite3
import hashlib
import os
import time
from payment_system import Wallet
from utils import Utility

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
            Utility.clear_screen()
            conn.close()
            return None

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if role == "1":
            role = "Freelancer"
            Utility.clear_screen()
            Utility.display_header("Create Your Freelancer Profile")
            name = input("Enter your name: ")
            skills = input("Enter your skills (comma separated): ")
            experience = input("Enter your experience: ")

            # Error handling for hourly rate
            while True:
                try:
                    hourly_rate = float(input("Enter your hourly rate: "))
                    if hourly_rate <= 0:
                        print("\nHourly rate must be greater than zero!")
                        time.sleep(1.5)
                        continue
                    break
                except ValueError:
                    print("\nInvalid input! Please enter a valid number for hourly rate.")
                    time.sleep(1.5)
                    
            payment_method = input("Enter your payment method: ")

            cursor.execute("""
                INSERT INTO users (username, password, role, name, skills, experience, hourly_rate, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (username, hashed_password, role, name, skills, experience, hourly_rate, payment_method))
        elif role == "2":
            role = "Employer"
            Utility.clear_screen()
            Utility.display_header("Create Your Employer Account")
            company_name = input("Enter your company name: ")

            cursor.execute("""
                INSERT INTO users (username, password, role, name, company_name)
                VALUES (?, ?, ?, ?, ?)""",
                (username, hashed_password, role, "N/A", company_name))  # Provide default "N/A" for name

        else:
            print("Invalid choice!")
            conn.close()
            return None

        # Get the last inserted ID
        user_id = cursor.lastrowid  

        # ✅ Create a wallet entry for the new user
        cursor.execute("INSERT INTO wallet (user_id, balance) VALUES (?, ?)", (user_id, 0.0))

        conn.commit()
        conn.close()

        print("\nSign-up successful! You can now log in.")
        time.sleep(1.5)
        Utility.clear_screen()

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
            time.sleep(1.5)
            Utility.clear_screen()

            # Extract only the necessary values
            user_id, username, password, role = user_data

            if role == "Freelancer":
                from freelancer import Freelancer
                return Freelancer(user_id, username, password, role)  # Pass only the expected values
            else:
                from employer import Employer
                return Employer(user_id, username, password, role)  # Pass only the expected values

        print("\nInvalid username or password!")
        time.sleep(1.5)
        Utility.clear_screen()
        return None
    
    def logout(self):
        print(f"\n{self.username} has logged out.")
        time.sleep(1.5)
        Utility.clear_screen()

    def wallet_menu(self):
        """Handles wallet balance and payment settings."""
        if not hasattr(self, "wallet"):  # Ensure wallet is initialized
            self.wallet = Wallet(self.username)

        while True:
            os.system("cls")
            self.wallet.balance = self.wallet.get_balance_from_db()  # ✅ Refresh balance from DB
            Utility.display_header("Wallet")
            print(f"Current Balance: Php {self.wallet.balance:.2f}\n")
            print("[1] Deposit Funds\n[2] Withdraw Funds\n[3] Back")
            Utility.divider()
            choice = input("Select an option: ").strip()

            if choice == "1":
                try:
                    amount = float(input("Enter deposit amount: "))
                    if amount > 0:
                        self.wallet.deposit(amount)
                    else:
                        print("\nDeposit amount must be greater than zero!")
                        time.sleep(1.5)
                except ValueError:
                    print("\nInvalid input! Please enter a valid number.")
                    time.sleep(1.5)
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
                break
            else:
                print("\nInvalid choice! Please try again.")
                time.sleep(1.5)
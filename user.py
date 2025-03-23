import sqlite3
import hashlib
import os
import time

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
            hourly_rate = float(input("Enter your hourly rate: "))
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
            time.sleep(2)
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
        time.sleep(2)
        Utility.clear_screen()
        return None
    
    @classmethod
    def logout(self):
        print(f"\n{self.username} has logged out.")
        time.sleep(2)

       
    @staticmethod
    def display_all_users():
        conn = sqlite3.connect("freelancer_marketplace.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()
       
        Utility.display_header("All Users")
        for user in users:
            print(user)
        Utility.divider()
   
    def logout(self):
        print(f"\n{self.username} has logged out.")
        time.sleep(2)
        Utility.clear_screen()
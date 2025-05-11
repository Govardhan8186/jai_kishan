import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class JaiKishanLoansApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jai Kishan Easy Loans for Farmers")
        self.root.geometry("1200x800")  # Reduced window size
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        # Initialize database connection
        self.db_connection = None
        self.db_config = {
            "host": "localhost",
            "user": "****",                #replace * with your mysql username
            "password": "*****",           #replace * with your mysql passwoard
            "database": "jai_kishan_loans"
        }
        
        # Initialize SMTP settings
        self.smtp_config = {
            "server": "smtp.gmail.com",
            "port": 587,
            "email": "**************@gmail.com",  # Replace with your email
            "password": "**** **** **** ****"     # Replace with your app password
        }
        
        # Initialize loans data
        self.loans_data = {}
        
        # Show login dialog first
        self.show_login_dialog()
        
    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))
        
    def send_verification_email(self, email, otp):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['email']
            msg['To'] = email
            msg['Subject'] = "Jai Kishan Loans - Email Verification"
            
            body = f"""
            <html>
                <body>
                    <h2>Email Verification</h2>
                    <p>Your OTP for email verification is: <strong>{otp}</strong></p>
                    <p>This OTP will expire in 5 minutes.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            server.starttls()
            server.login(self.smtp_config['email'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
            
    def verify_email(self, email, dialog):
        otp = self.generate_otp()
        if self.send_verification_email(email, otp):
            verify_dialog = ctk.CTkToplevel(dialog)
            verify_dialog.title("Email Verification")
            verify_dialog.geometry("400x200")
            verify_dialog.transient(dialog)
            verify_dialog.grab_set()
            
            # OTP Entry
            otp_frame = ctk.CTkFrame(verify_dialog)
            otp_frame.pack(fill="x", padx=20, pady=20)
            otp_label = ctk.CTkLabel(otp_frame, text="Enter OTP:", width=100)
            otp_label.pack(side="left", padx=5)
            otp_entry = ctk.CTkEntry(otp_frame, width=200)
            otp_entry.pack(side="left", padx=5)
            
            def verify():
                if otp_entry.get() == otp:
                    verify_dialog.destroy()
                    self.signup(dialog)
                else:
                    messagebox.showerror("Error", "Invalid OTP")
            
            # Verify button
            verify_button = ctk.CTkButton(
                verify_dialog,
                text="Verify",
                command=verify,
                fg_color="#2e7d32",
                hover_color="#1b5e20",
                width=200,
                height=40,
                font=("Helvetica", 16, "bold")
            )
            verify_button.pack(pady=20)
            
            # Wait for verification
            dialog.wait_window(verify_dialog)
        else:
            messagebox.showerror("Error", "Failed to send verification email")
            
    def show_login_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Jai Kishan Loans - Login/Signup")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create tab control with custom style
        style = ttk.Style()
        style.configure("Custom.TNotebook", tabmargins=[10, 5, 10, 0])  # Increased tab margins
        style.configure("Custom.TNotebook.Tab", 
                      padding=[30, 10],  # Increased padding
                      font=("Helvetica", 14, "bold"))  # Larger font
        
        tab_control = ttk.Notebook(dialog, style="Custom.TNotebook")
        
        # Login Tab
        login_tab = ctk.CTkFrame(tab_control)
        tab_control.add(login_tab, text="Login")
        
        # Signup Tab
        signup_tab = ctk.CTkFrame(tab_control)
        tab_control.add(signup_tab, text="Create Account")
        
        tab_control.pack(expand=1, fill="both", padx=20, pady=20)
        
        # Setup Login Tab
        self.setup_login_tab(login_tab)
        
        # Setup Signup Tab
        self.setup_signup_tab(signup_tab)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        
    def setup_login_tab(self, tab):
        # Title
        title_label = ctk.CTkLabel(
            tab,
            text="Login to Jai Kishan Loans",
            font=("Helvetica", 24, "bold"),
            text_color="#1b5e20"
        )
        title_label.pack(pady=30)
        
        # Username
        user_frame = ctk.CTkFrame(tab)
        user_frame.pack(fill="x", padx=30, pady=10)
        user_label = ctk.CTkLabel(user_frame, text="Username:", width=100)
        user_label.pack(side="left", padx=5)
        self.login_user_entry = ctk.CTkEntry(user_frame, width=250)
        self.login_user_entry.pack(side="left", padx=5)
        
        # Password
        pass_frame = ctk.CTkFrame(tab)
        pass_frame.pack(fill="x", padx=30, pady=10)
        pass_label = ctk.CTkLabel(pass_frame, text="Password:", width=100)
        pass_label.pack(side="left", padx=5)
        self.login_pass_entry = ctk.CTkEntry(pass_frame, width=250, show="*")
        self.login_pass_entry.pack(side="left", padx=5)
        
        # Login button
        login_button = ctk.CTkButton(
            tab,
            text="Login",
            command=self.login,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            width=300,  # Increased button width
            height=40,  # Increased button height
            font=("Helvetica", 16, "bold")  # Larger font
        )
        login_button.pack(pady=30)
        
    def setup_signup_tab(self, tab):
        # Title
        title_label = ctk.CTkLabel(
            tab,
            text="Create New Account",
            font=("Helvetica", 24, "bold"),
            text_color="#1b5e20"
        )
        title_label.pack(pady=20)
        
        # Full Name
        name_frame = ctk.CTkFrame(tab)
        name_frame.pack(fill="x", padx=30, pady=10)
        name_label = ctk.CTkLabel(name_frame, text="Full Name:", width=100)
        name_label.pack(side="left", padx=5)
        self.signup_name_entry = ctk.CTkEntry(name_frame, width=250)
        self.signup_name_entry.pack(side="left", padx=5)
        
        # Email
        email_frame = ctk.CTkFrame(tab)
        email_frame.pack(fill="x", padx=30, pady=10)
        email_label = ctk.CTkLabel(email_frame, text="Email:", width=100)
        email_label.pack(side="left", padx=5)
        self.signup_email_entry = ctk.CTkEntry(email_frame, width=250)
        self.signup_email_entry.pack(side="left", padx=5)
        
        # Username
        user_frame = ctk.CTkFrame(tab)
        user_frame.pack(fill="x", padx=30, pady=10)
        user_label = ctk.CTkLabel(user_frame, text="Username:", width=100)
        user_label.pack(side="left", padx=5)
        self.signup_user_entry = ctk.CTkEntry(user_frame, width=250)
        self.signup_user_entry.pack(side="left", padx=5)
        
        # Password
        pass_frame = ctk.CTkFrame(tab)
        pass_frame.pack(fill="x", padx=30, pady=10)
        pass_label = ctk.CTkLabel(pass_frame, text="Password:", width=100)
        pass_label.pack(side="left", padx=5)
        self.signup_pass_entry = ctk.CTkEntry(pass_frame, width=250, show="*")
        self.signup_pass_entry.pack(side="left", padx=5)
        
        # Confirm Password
        confirm_frame = ctk.CTkFrame(tab)
        confirm_frame.pack(fill="x", padx=30, pady=10)
        confirm_label = ctk.CTkLabel(confirm_frame, text="Confirm Password:", width=100)
        confirm_label.pack(side="left", padx=5)
        self.signup_confirm_entry = ctk.CTkEntry(confirm_frame, width=250, show="*")
        self.signup_confirm_entry.pack(side="left", padx=5)
        
        # Signup button
        signup_button = ctk.CTkButton(
            tab,
            text="Create Account",
            command=lambda: self.verify_email(self.signup_email_entry.get().strip(), tab),
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            width=300,
            height=40,
            font=("Helvetica", 16, "bold")
        )
        signup_button.pack(pady=30)
        
    def login(self):
        username = self.login_user_entry.get().strip()
        password = self.login_pass_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        try:
            # First try to connect to MySQL server without database
            conn = mysql.connector.connect(
                host=self.db_config["host"],
                user=self.db_config["user"],
                password=self.db_config["password"]
            )
            
            cursor = conn.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']}")
            cursor.execute(f"USE {self.db_config['database']}")
            
            # Create users table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    password VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create farmers table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS farmers (
                    farmer_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    village VARCHAR(100) NOT NULL,
                    district VARCHAR(100) NOT NULL,
                    loan_amount DECIMAL(10,2) NOT NULL,
                    interest_rate DECIMAL(4,2) NOT NULL,
                    loan_date DATE NOT NULL,
                    repayment_date DATE NOT NULL,
                    status VARCHAR(20) DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create loan_applications table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loan_applications (
                    application_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    age INT NOT NULL,
                    aadhar_number VARCHAR(12) NOT NULL,
                    village VARCHAR(100) NOT NULL,
                    district VARCHAR(100) NOT NULL,
                    loan_amount DECIMAL(10,2) NOT NULL,
                    purpose VARCHAR(200) NOT NULL,
                    land_area DECIMAL(10,2) NOT NULL,
                    land_type VARCHAR(50) NOT NULL,
                    status VARCHAR(20) DEFAULT 'Pending',
                    application_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            # Now connect to the specific database
            self.db_connection = mysql.connector.connect(
                host=self.db_config["host"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                database=self.db_config["database"]
            )
            
            # Check if user exists and password matches
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, name FROM users 
                WHERE username = %s AND password = %s
            """, (username, password))
            
            result = cursor.fetchone()
            
            if result:
                user_id, user_name = result
                
                # Store the current user's information
                self.current_user = {
                    "id": user_id,
                    "name": user_name,
                    "username": username
                }
                
                # Close login dialog and destroy it
                for widget in self.root.winfo_children():
                    if isinstance(widget, ctk.CTkToplevel):
                        widget.destroy()
                
                # Clear any existing widgets in main window
                for widget in self.root.winfo_children():
                    widget.destroy()
                
                # Setup main application window
                self.setup_gui()
                
                # Load and update data
                self.loans_data = self.load_loans_data()
                self.update_farmer_list()
                self.update_reports()
                
                messagebox.showinfo("Success", f"Welcome, {user_name}!")
            else:
                messagebox.showerror("Error", "Invalid username or password")
                
        except Error as e:
            if e.errno == 1045:  # Access denied error
                messagebox.showerror("Database Error", "Access denied. Please check your username and password.")
            elif e.errno == 2003:  # Connection error
                messagebox.showerror("Database Error", "Could not connect to MySQL server. Please check if MySQL is running.")
            else:
                messagebox.showerror("Database Error", f"Error: {str(e)}")

    def load_loans_data(self):
        try:
            if not self.db_connection or not self.db_connection.is_connected():
                self.db_connection = mysql.connector.connect(
                    host=self.db_config["host"],
                    user=self.db_config["user"],
                    password=self.db_config["password"],
                    database=self.db_config["database"]
                )
            
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM farmers")
            farmers = cursor.fetchall()
            
            loans_data = {}
            for farmer in farmers:
                farmer_id = f"Farmer{farmer['farmer_id']}"
                loans_data[farmer_id] = {
                    "name": farmer["name"],
                    "age": farmer["age"],
                    "village": farmer["village"],
                    "district": farmer["district"],
                    "loan_amount": float(farmer["loan_amount"]),
                    "interest_rate": float(farmer["interest_rate"]),
                    "loan_date": farmer["loan_date"].strftime("%Y-%m-%d"),
                    "repayment_date": farmer["repayment_date"].strftime("%Y-%m-%d"),
                    "status": farmer["status"]
                }
            return loans_data
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading data: {str(e)}")
            return {}
            
    def signup(self, dialog):
        name = self.signup_name_entry.get().strip()
        email = self.signup_email_entry.get().strip()
        username = self.signup_user_entry.get().strip()
        password = self.signup_pass_entry.get().strip()
        confirm_password = self.signup_confirm_entry.get().strip()
        
        if not all([name, email, username, password, confirm_password]):
            messagebox.showerror("Error", "All fields are required")
            return
            
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
            
        try:
            # Connect to database
            conn = mysql.connector.connect(
                host=self.db_config["host"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                database=self.db_config["database"]
            )
            
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                return
                
            # Check if email already exists
            cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Email already registered")
                return
            
            # Insert new user
            cursor.execute("""
                INSERT INTO users (name, email, username, password)
                VALUES (%s, %s, %s, %s)
            """, (name, email, username, password))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Account created successfully! Please login.")
            dialog.destroy()
            
        except Error as e:
            messagebox.showerror("Signup Error", f"Failed to create account: {str(e)}")
            
    def setup_gui(self):
        # Create main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create header frame
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Jai Kishan Easy Loans for Farmers",
            font=("Helvetica", 24, "bold"),
            text_color="#1b5e20"
        )
        title_label.pack(side="left", padx=20)
        
        # Logout button
        logout_button = ctk.CTkButton(
            header_frame,
            text="Logout",
            command=self.logout,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            width=100,
            height=40,
            font=("Helvetica", 14, "bold")
        )
        logout_button.pack(side="right", padx=20)
        
        # Create tabs with custom style
        style = ttk.Style()
        style.configure("Custom.TNotebook", tabmargins=[10, 5, 10, 0])
        style.configure("Custom.TNotebook.Tab", 
                      padding=[30, 10],
                      font=("Helvetica", 16, "bold"),
                      width=20)  # Increased tab width
        
        self.tab_control = ttk.Notebook(self.main_frame, style="Custom.TNotebook")
        
        # Loan Application Tab
        application_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(application_tab, text="Loan Application")
        
        # Loan Management Tab
        loan_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(loan_tab, text="Loan Management")
        
        # Farmer List Tab
        farmer_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(farmer_tab, text="Farmer List")
        
        # Reports Tab
        reports_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(reports_tab, text="Reports")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Setup Loan Application Tab
        self.setup_loan_application_tab(application_tab)
        
        # Setup Loan Management Tab
        self.setup_loan_management_tab(loan_tab)
        
        # Setup Farmer List Tab
        self.setup_farmer_list_tab(farmer_tab)
        
        # Setup Reports Tab
        self.setup_reports_tab(reports_tab)
        
        # Set default tab to Loan Application
        self.tab_control.select(0)
        
    def setup_loan_application_tab(self, tab):
        # Create main container with scrollbar
        main_container = ctk.CTkFrame(tab)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)
        
        # Configure canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create form frame
        form_frame = ctk.CTkFrame(scrollable_frame)
        form_frame.pack(fill="x", padx=20, pady=20)
        
        # Application Title
        title_label = ctk.CTkLabel(
            form_frame,
            text="New Loan Application",
            font=("Helvetica", 24, "bold"),
            text_color="#1b5e20"
        )
        title_label.pack(pady=20)
        
        # Personal Details Section
        personal_frame = ctk.CTkFrame(form_frame)
        personal_frame.pack(fill="x", padx=20, pady=10)
        
        personal_label = ctk.CTkLabel(
            personal_frame,
            text="Personal Details",
            font=("Helvetica", 18, "bold")
        )
        personal_label.pack(pady=10)
        
        # Name
        name_frame = ctk.CTkFrame(personal_frame)
        name_frame.pack(fill="x", padx=20, pady=10)
        name_label = ctk.CTkLabel(name_frame, text="Full Name:", width=120, font=("Helvetica", 14))
        name_label.pack(side="left", padx=5)
        self.app_name_entry = ctk.CTkEntry(name_frame, width=400, height=40, font=("Helvetica", 14))
        self.app_name_entry.pack(side="left", padx=5)
        
        # Age
        age_frame = ctk.CTkFrame(personal_frame)
        age_frame.pack(fill="x", padx=20, pady=10)
        age_label = ctk.CTkLabel(age_frame, text="Age:", width=120, font=("Helvetica", 14))
        age_label.pack(side="left", padx=5)
        self.app_age_entry = ctk.CTkEntry(age_frame, width=200, height=40, font=("Helvetica", 14))
        self.app_age_entry.pack(side="left", padx=5)
        
        # Aadhar Number
        aadhar_frame = ctk.CTkFrame(personal_frame)
        aadhar_frame.pack(fill="x", padx=20, pady=10)
        aadhar_label = ctk.CTkLabel(aadhar_frame, text="Aadhar Number:", width=120, font=("Helvetica", 14))
        aadhar_label.pack(side="left", padx=5)
        self.aadhar_entry = ctk.CTkEntry(aadhar_frame, width=300, height=40, font=("Helvetica", 14))
        self.aadhar_entry.pack(side="left", padx=5)
        
        # Address Details Section
        address_frame = ctk.CTkFrame(form_frame)
        address_frame.pack(fill="x", padx=20, pady=20)
        
        address_label = ctk.CTkLabel(
            address_frame,
            text="Address Details",
            font=("Helvetica", 18, "bold")
        )
        address_label.pack(pady=10)
        
        # Village
        village_frame = ctk.CTkFrame(address_frame)
        village_frame.pack(fill="x", padx=20, pady=10)
        village_label = ctk.CTkLabel(village_frame, text="Village:", width=120, font=("Helvetica", 14))
        village_label.pack(side="left", padx=5)
        self.app_village_entry = ctk.CTkEntry(village_frame, width=400, height=40, font=("Helvetica", 14))
        self.app_village_entry.pack(side="left", padx=5)
        
        # District
        district_frame = ctk.CTkFrame(address_frame)
        district_frame.pack(fill="x", padx=20, pady=10)
        district_label = ctk.CTkLabel(district_frame, text="District:", width=120, font=("Helvetica", 14))
        district_label.pack(side="left", padx=5)
        self.app_district_entry = ctk.CTkEntry(district_frame, width=400, height=40, font=("Helvetica", 14))
        self.app_district_entry.pack(side="left", padx=5)
        
        # Loan Details Section
        loan_frame = ctk.CTkFrame(form_frame)
        loan_frame.pack(fill="x", padx=20, pady=20)
        
        loan_label = ctk.CTkLabel(
            loan_frame,
            text="Loan Details",
            font=("Helvetica", 18, "bold")
        )
        loan_label.pack(pady=10)
        
        # Loan Amount
        amount_frame = ctk.CTkFrame(loan_frame)
        amount_frame.pack(fill="x", padx=20, pady=10)
        amount_label = ctk.CTkLabel(amount_frame, text="Loan Amount (₹):", width=120, font=("Helvetica", 14))
        amount_label.pack(side="left", padx=5)
        self.app_amount_entry = ctk.CTkEntry(amount_frame, width=300, height=40, font=("Helvetica", 14))
        self.app_amount_entry.pack(side="left", padx=5)
        
        # Loan Purpose
        purpose_frame = ctk.CTkFrame(loan_frame)
        purpose_frame.pack(fill="x", padx=20, pady=10)
        purpose_label = ctk.CTkLabel(purpose_frame, text="Loan Purpose:", width=120, font=("Helvetica", 14))
        purpose_label.pack(side="left", padx=5)
        self.app_purpose_entry = ctk.CTkEntry(purpose_frame, width=400, height=40, font=("Helvetica", 14))
        self.app_purpose_entry.pack(side="left", padx=5)
        
        # Land Area
        land_area_frame = ctk.CTkFrame(loan_frame)
        land_area_frame.pack(fill="x", padx=20, pady=10)
        land_area_label = ctk.CTkLabel(land_area_frame, text="Land Area (acres):", width=120, font=("Helvetica", 14))
        land_area_label.pack(side="left", padx=5)
        self.app_land_area_entry = ctk.CTkEntry(land_area_frame, width=200, height=40, font=("Helvetica", 14))
        self.app_land_area_entry.pack(side="left", padx=5)
        
        # Land Type
        land_type_frame = ctk.CTkFrame(loan_frame)
        land_type_frame.pack(fill="x", padx=20, pady=10)
        land_type_label = ctk.CTkLabel(land_type_frame, text="Land Type:", width=120, font=("Helvetica", 14))
        land_type_label.pack(side="left", padx=5)
        self.app_land_type_entry = ctk.CTkEntry(land_type_frame, width=200, height=40, font=("Helvetica", 14))
        self.app_land_type_entry.pack(side="left", padx=5)
        
        # Submit and Clear buttons
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(fill="x", padx=20, pady=30)
        
        submit_button = ctk.CTkButton(
            button_frame,
            text="Submit Loan",
            command=self.submit_loan_application,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            width=200,
            height=50,
            font=("Helvetica", 16, "bold")
        )
        submit_button.pack(side="left", padx=20)
        
        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear Form",
            command=self.clear_application_form,
            fg_color="#f44336",
            hover_color="#d32f2f",
            width=200,
            height=50,
            font=("Helvetica", 16, "bold")
        )
        clear_button.pack(side="left", padx=20)
        
    def submit_loan_application(self):
        try:
            # Get form data
            name = self.app_name_entry.get().strip()
            age = int(self.app_age_entry.get())
            aadhar = self.aadhar_entry.get().strip()
            village = self.app_village_entry.get().strip()
            district = self.app_district_entry.get().strip()
            loan_amount = float(self.app_amount_entry.get())
            purpose = self.app_purpose_entry.get().strip()
            land_area = float(self.app_land_area_entry.get())
            land_type = self.app_land_type_entry.get().strip()
            
            # Validate data
            if not all([name, aadhar, village, district, purpose, land_type]):
                raise ValueError("All fields are required")
            
            # Save to database
            cursor = self.db_connection.cursor()
            query = """
                INSERT INTO loan_applications 
                (name, age, aadhar_number, village, district, loan_amount, 
                 purpose, land_area, land_type, status, application_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (name, age, aadhar, village, district, loan_amount,
                     purpose, land_area, land_type, "Pending", datetime.now().strftime("%Y-%m-%d"))
            
            cursor.execute(query, values)
            self.db_connection.commit()
            
            # Clear form
            self.clear_application_form()
            
            # Show success message
            messagebox.showinfo("Success", "Loan application submitted successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Error as e:
            messagebox.showerror("Database Error", f"Error submitting application: {e}")
            
    def clear_application_form(self):
        self.app_name_entry.delete(0, tk.END)
        self.app_age_entry.delete(0, tk.END)
        self.aadhar_entry.delete(0, tk.END)
        self.app_village_entry.delete(0, tk.END)
        self.app_district_entry.delete(0, tk.END)
        self.app_amount_entry.delete(0, tk.END)
        self.app_purpose_entry.delete(0, tk.END)
        self.app_land_area_entry.delete(0, tk.END)
        self.app_land_type_entry.delete(0, tk.END)
        
    def setup_loan_management_tab(self, tab):
        # Create form frame
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Farmer Details
        farmer_label = ctk.CTkLabel(form_frame, text="Farmer Details", font=("Helvetica", 16, "bold"))
        farmer_label.pack(pady=10)
        
        # Name
        name_frame = ctk.CTkFrame(form_frame)
        name_frame.pack(fill="x", padx=10, pady=5)
        name_label = ctk.CTkLabel(name_frame, text="Name:", width=100)
        name_label.pack(side="left", padx=5)
        self.name_entry = ctk.CTkEntry(name_frame, width=300)
        self.name_entry.pack(side="left", padx=5)
        
        # Age
        age_frame = ctk.CTkFrame(form_frame)
        age_frame.pack(fill="x", padx=10, pady=5)
        age_label = ctk.CTkLabel(age_frame, text="Age:", width=100)
        age_label.pack(side="left", padx=5)
        self.age_entry = ctk.CTkEntry(age_frame, width=100)
        self.age_entry.pack(side="left", padx=5)
        
        # Village
        village_frame = ctk.CTkFrame(form_frame)
        village_frame.pack(fill="x", padx=10, pady=5)
        village_label = ctk.CTkLabel(village_frame, text="Village:", width=100)
        village_label.pack(side="left", padx=5)
        self.village_entry = ctk.CTkEntry(village_frame, width=300)
        self.village_entry.pack(side="left", padx=5)
        
        # District
        district_frame = ctk.CTkFrame(form_frame)
        district_frame.pack(fill="x", padx=10, pady=5)
        district_label = ctk.CTkLabel(district_frame, text="District:", width=100)
        district_label.pack(side="left", padx=5)
        self.district_entry = ctk.CTkEntry(district_frame, width=300)
        self.district_entry.pack(side="left", padx=5)
        
        # Loan Details
        loan_label = ctk.CTkLabel(form_frame, text="Loan Details", font=("Helvetica", 16, "bold"))
        loan_label.pack(pady=10)
        
        # Loan Amount
        amount_frame = ctk.CTkFrame(form_frame)
        amount_frame.pack(fill="x", padx=10, pady=5)
        amount_label = ctk.CTkLabel(amount_frame, text="Loan Amount:", width=100)
        amount_label.pack(side="left", padx=5)
        self.amount_entry = ctk.CTkEntry(amount_frame, width=200)
        self.amount_entry.pack(side="left", padx=5)
        
        # Interest Rate
        interest_frame = ctk.CTkFrame(form_frame)
        interest_frame.pack(fill="x", padx=10, pady=5)
        interest_label = ctk.CTkLabel(interest_frame, text="Interest Rate:", width=100)
        interest_label.pack(side="left", padx=5)
        self.interest_entry = ctk.CTkEntry(interest_frame, width=100)
        self.interest_entry.pack(side="left", padx=5)
        self.interest_entry.insert(0, "4.0")  # Default interest rate
        
        # Loan Date
        loan_date_frame = ctk.CTkFrame(form_frame)
        loan_date_frame.pack(fill="x", padx=10, pady=5)
        loan_date_label = ctk.CTkLabel(loan_date_frame, text="Loan Date:", width=100)
        loan_date_label.pack(side="left", padx=5)
        self.loan_date_entry = ctk.CTkEntry(loan_date_frame, width=200)
        self.loan_date_entry.pack(side="left", padx=5)
        self.loan_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Repayment Date
        repayment_frame = ctk.CTkFrame(form_frame)
        repayment_frame.pack(fill="x", padx=10, pady=5)
        repayment_label = ctk.CTkLabel(repayment_frame, text="Repayment Date:", width=100)
        repayment_label.pack(side="left", padx=5)
        self.repayment_entry = ctk.CTkEntry(repayment_frame, width=200)
        self.repayment_entry.pack(side="left", padx=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(fill="x", padx=10, pady=20)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Loan",
            command=self.save_loan,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        save_button.pack(side="left", padx=5)
        
        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear Form",
            command=self.clear_form,
            fg_color="#f44336",
            hover_color="#d32f2f"
        )
        clear_button.pack(side="left", padx=5)
        
    def setup_farmer_list_tab(self, tab):
        # Create table frame with padding
        table_frame = ctk.CTkFrame(tab)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create treeview with larger size
        columns = ("Name", "Age", "Village", "District", "Loan Amount", "Interest Rate", "Loan Date", "Repayment Date", "Status")
        self.farmer_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        # Define headings with larger width and font
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 14))  # Increased font size
        style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))  # Increased font size
        
        # Configure column widths
        column_widths = {
            "Name": 200,
            "Age": 80,
            "Village": 200,
            "District": 200,
            "Loan Amount": 150,
            "Interest Rate": 120,
            "Loan Date": 150,
            "Repayment Date": 150,
            "Status": 100
        }
        
        for col in columns:
            self.farmer_tree.heading(col, text=col)
            self.farmer_tree.column(col, width=column_widths[col], anchor="center")  # Center align all columns
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.farmer_tree.yview)
        self.farmer_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the treeview and scrollbar
        self.farmer_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add some padding around the table
        table_frame.pack_propagate(False)
        table_frame.configure(height=700)  # Increased height
        
        # Populate the treeview
        self.update_farmer_list()
        
    def setup_reports_tab(self, tab):
        # Create reports frame
        reports_frame = ctk.CTkFrame(tab)
        reports_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Total Loans
        total_loans_frame = ctk.CTkFrame(reports_frame)
        total_loans_frame.pack(fill="x", padx=10, pady=10)
        
        total_loans_label = ctk.CTkLabel(total_loans_frame, text="Total Active Loans:", font=("Helvetica", 16, "bold"))
        total_loans_label.pack(side="left", padx=5)
        
        self.total_loans_value = ctk.CTkLabel(total_loans_frame, text="0", font=("Helvetica", 16))
        self.total_loans_value.pack(side="left", padx=5)
        
        # Total Loan Amount
        total_amount_frame = ctk.CTkFrame(reports_frame)
        total_amount_frame.pack(fill="x", padx=10, pady=10)
        
        total_amount_label = ctk.CTkLabel(total_amount_frame, text="Total Loan Amount:", font=("Helvetica", 16, "bold"))
        total_amount_label.pack(side="left", padx=5)
        
        self.total_amount_value = ctk.CTkLabel(total_amount_frame, text="₹0", font=("Helvetica", 16))
        self.total_amount_value.pack(side="left", padx=5)
        
        # Update reports
        self.update_reports()
        
    def save_loan(self):
        try:
            # Get form data
            name = self.name_entry.get().strip()
            age = int(self.age_entry.get())
            village = self.village_entry.get().strip()
            district = self.district_entry.get().strip()
            loan_amount = float(self.amount_entry.get())
            interest_rate = float(self.interest_entry.get())
            loan_date = self.loan_date_entry.get()
            repayment_date = self.repayment_entry.get()
            
            # Validate data
            if not all([name, village, district, loan_date, repayment_date]):
                raise ValueError("All fields are required")
            
            # Save to database
            cursor = self.db_connection.cursor()
            query = """
                INSERT INTO farmers 
                (name, age, village, district, loan_amount, interest_rate, loan_date, repayment_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (name, age, village, district, loan_amount, interest_rate, 
                     loan_date, repayment_date, "Active")
            
            cursor.execute(query, values)
            self.db_connection.commit()
            
            # Get the new farmer ID
            farmer_id = cursor.lastrowid
            
            # Update local data
            farmer_key = f"Farmer{farmer_id}"
            self.loans_data[farmer_key] = {
                "name": name,
                "age": age,
                "village": village,
                "district": district,
                "loan_amount": loan_amount,
                "interest_rate": interest_rate,
                "loan_date": loan_date,
                "repayment_date": repayment_date,
                "status": "Active"
            }
            
            # Update displays
            self.update_farmer_list()
            self.update_reports()
            self.clear_form()
            
            messagebox.showinfo("Success", "Loan saved successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Error as e:
            messagebox.showerror("Database Error", f"Error saving loan: {e}")
            
    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.village_entry.delete(0, tk.END)
        self.district_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.interest_entry.delete(0, tk.END)
        self.interest_entry.insert(0, "4.0")
        self.loan_date_entry.delete(0, tk.END)
        self.loan_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.repayment_entry.delete(0, tk.END)
        
    def update_farmer_list(self):
        # Clear existing items
        for item in self.farmer_tree.get_children():
            self.farmer_tree.delete(item)
            
        # Add new items
        for farmer_id, data in self.loans_data.items():
            self.farmer_tree.insert("", "end", values=(
                data["name"],
                data["age"],
                data["village"],
                data["district"],
                f"₹{data['loan_amount']:,.2f}",  # Format with commas and 2 decimal places
                f"{data['interest_rate']}%",
                data["loan_date"],
                data["repayment_date"],
                data["status"]
            ))
            
    def update_reports(self):
        # Calculate total loans and amount
        total_loans = len(self.loans_data)
        total_amount = sum(data["loan_amount"] for data in self.loans_data.values())
        
        # Update labels
        self.total_loans_value.configure(text=str(total_loans))
        self.total_amount_value.configure(text=f"₹{total_amount:,.2f}")

    def logout(self):
        # Close database connection
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()
            print("Database connection closed")
        
        # Show login dialog again
        self.show_login_dialog()
        
        # Refresh data
        self.loans_data = self.load_loans_data()
        self.update_farmer_list()
        self.update_reports()
        
        # Switch to Loan Management tab
        self.tab_control.select(1)

    def __del__(self):
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    root = ctk.CTk()
    app = JaiKishanLoansApp(root)
    root.mainloop() 
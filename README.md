## To-do-App
A full-stack to-do application with automated email reminders. The application includes user authentication, complete CRUD operations, and a background job scheduler for sending email reminders 30 minutes before task due times.

# Tech Stack used: 

Frontend - HTML5, CSS3, JavaScript

Backend - 
  1. Python 3.8+ - Core Programming Language
  2. Flask 3.0 - Lightweight Web Framework
  3. Flask Login - User session management
  4. Flask Mail - Email sending functionality
  5. APScheduler - Background job scheduling
     
Database -
  1. MySQL Workbench 8.0 - Relational database
  2. SQLAlchemy - ORM (Object Relational Mapper) for database operations
  3. PyMySQL - MySQL database connector

# Architecture Overview: 
The web application is divided into two main components - the primary web application flow and background job processing. On the front end, users interact through a browser using HTML, CSS, and JavaScript, which communicates with a Flask server via HTTP. The Flask server, built in Python, handles requests and connects to a MySQL database using SQL for data storage and retrieval. The database serves as a shared resource between the server and MySQL. Separately, background jobs are managed by APScheduler, which automates tasks like sending emails and reminders, ensuring asynchronous operations run smoothly without interrupting the main application flow. This setup highlights a clean separation between user-facing interactions and backend automation.

# Installation & Setup:
# Pre-requisites - Python 3.8+, MySQL Server, pip (Python Package Manager)

# Step 01: Create a project directory titled 'to-do app' and add all the files.
  1. app.py
  2. models.py
  3. scheduler.py
  4. config.py
  5. requirements.txt
  6. init.sql
  7. templates
       a) index.html
       b) dashboard.html 

# Step 02: In your command prompt, create virtual environment.

 #Navigate to project directory
 cd todo-app
 
 #Create virtual environment
 python -m venv venv
 
 #Activate virtual environment
 
 #On Windows:
 venv\Scripts\activate
 
 #On macOS/Linux:
 source venv/bin/activate

# Step 03: Install dependencies.
  Type 'pip install -r requirements.txt'.

# Step 04: Setup MySQL database.
  1. Start MySQL Server -
     #Windows: Start MySQL service from Services
     #MacOS: brew services start mysql
     #Linux: sudo system ctl start mysql
  2. Login to MySQL -
     Type 'mysql -u root -p'
  3. Run the initialization script
     source init.sql;
     --OR Manually create database:
     CREATE DATABASE todo_app;
  4. Update database crendentials in app.py
      app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://username:password@localhost/todo_app' (Add your username and root password)
     
# Step 05: Configure email settings - Using Gmail.
  1. Enable 2-Factor Authentication in your Google Account.
  2. Generate App password:
     Go to Google Account --> Security --> 2-step verification
     Scroll to "App passwords"
     Generate password
  3. Update app.py
     app.config['MAIL_USERNAME'] = 'your-email@gmail.com' //type your email
     app.config['MAIL_PASSWORD'] = 'your-16-digit-app-password' //copy paste the generated password
     app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com' //type your email

# Step 06: Run the application.
Type 'python app.py' in your command prompt
OR run the app.py file in VS Code (If accessing through VS Code!)
  The application will create database tables automatically.
  Start the Flask server on http://localhost:5000
  Initialize the background scheduler for email reminders 

# Step 07: Access the Application.
  Open your browser and navigate to 'http://localhost:5000'

# Usage Guide:

1. Sign Up -
   Click "Sign Up" tab
   Enter your name, email & password
   Click "Sign Up" button
2. Login -
   Now, enter your email and password
   Click "Login" button
3. Create Tasks -
   Fill in the task title (required)
   Add description (optional)
   Set due date and time (optional)
   Click "Add Task"
4. Manage Tasks -
   Mark Complete: Check the checkbox
   Edit Task: Click "Edit" button
   Delete Task: Click "Delete" button
   Filter Tasks: Use "All", "Pending", "Completed" buttons
5. Email Reminders -
   Set a due date when creating a task
   System checks every 5 minutes
   Sends email 30 minutes before the due time
   Only sends once per task

# Project Workflow:
  Authentication FLow -
  1. Sign Up - User Input --> Password Hashing --> Store in MySQL
  2. Login - User Input --> Hash Verification --> Flask Login session --> Dashboard
  3. Session Management - Flask Logins manages user session with cookies, @login_required decorator protects routes

  Task Management Flow -
  1 CREATE Task

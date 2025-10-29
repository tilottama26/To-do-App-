# To-do-App
A full-stack to-do application with automated email reminders. The application includes user authentication, complete CRUD operations, and a background job scheduler for sending email reminders 30 minutes before task due times.

## Tech Stack used: 

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

## Architecture Overview: 
The web application is divided into two main components - the primary web application flow and background job processing. On the front end, users interact through a browser using HTML, CSS, and JavaScript, which communicates with a Flask server via HTTP. The Flask server, built in Python, handles requests and connects to a MySQL database using SQL for data storage and retrieval. The database serves as a shared resource between the server and MySQL. Separately, background jobs are managed by APScheduler, which automates tasks like sending emails and reminders, ensuring asynchronous operations run smoothly without interrupting the main application flow. This setup highlights a clean separation between user-facing interactions and backend automation.

## Features:

### Frontend Features:

1. Responsive Design -
   Mobile-friendly with CSS Grid and Flexbox.
   Breakpoints for tablets and phones. 
2. User Experience -
   Smooth animations and transitions.
   Real-time task filtering.
   Inline editing with modal.
   Color-coded task status.
   Overdue task highlighting.
3. API Communication -
   RESTful API design.
   JSON data format.
   Async/await pattern for smooth UX.
   Error handling with user feedback.

### Security Features:
  1. Each user only sees their own tasks.
  2. Secure cookies with Flask-Login for session management.
  3. Built into Flask forms.
  4. SQLAlchemy ORM parameterized queries for SQL Injection prevention.

## Folder Structure:

``` 
TODO-APP/
  |-- __pycache__/
  |    |__ models.cpython-312.pyc
  |    |__ scheduler.cpython-312.pyc
  |-- templates/
      |__ dashboard.html
      |__ index.html
  |-- venv/
  |-- app.py/
  |-- models.py/
  |-- requirements.txt/
  |-- scheduler.py
```

## Installation & Setup:
### Pre-requisites - Python 3.8+, MySQL Server, pip (Python Package Manager)

### Step 01: Create a project directory titled 'to-do app' and add all the files.
  1. app.py
  2. models.py
  3. scheduler.py
  4. config.py
  5. requirements.txt
  6. init.sql
  7. templates
       a) index.html
       b) dashboard.html 

### Step 02: In your command prompt, create virtual environment.

 #Navigate to project directory
 cd todo-app
 
 #Create virtual environment
 python -m venv venv
 
 #Activate virtual environment
 
 #On Windows:
 venv\Scripts\activate
 
 #On macOS/Linux:
 source venv/bin/activate

### Step 03: Install dependencies.
  Type 'pip install -r requirements.txt'.

### Step 04: Setup MySQL database.
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
     
### Step 05: Configure email settings - Using Gmail.
  1. Enable 2-Factor Authentication in your Google Account.
  2. Generate App password:
     Go to Google Account --> Security --> 2-step verification
     Scroll to "App passwords"
     Generate password
  3. Update app.py
     app.config['MAIL_USERNAME'] = 'your-email@gmail.com' //type your email
     app.config['MAIL_PASSWORD'] = 'your-16-digit-app-password' //copy paste the generated password
     app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com' //type your email

### Step 06: Run the application.
Type 'python app.py' in your command prompt
OR run the app.py file in VS Code (If accessing through VS Code!)
  The application will create database tables automatically.
  Start the Flask server on http://localhost:5000
  Initialize the background scheduler for email reminders 

### Step 07: Access the Application.
  Open your browser and navigate to 'http://localhost:5000'

## Usage Guide:

1. Sign Up -
   a) Click "Sign Up" tab.
   b) Enter your name, email & password.
   c) Click "Sign Up" button.
2. Login -
   a) Now, enter your email and password.
   b) Click "Login" button
3. Create Tasks -
   a) Fill in the task title (required).
   b) Add description (optional).
   c) Set due date and time (optional).
   d) Click "Add Task".
4. Manage Tasks -
   a) Mark Complete: Check the checkbox.
   b) Edit Task: Click "Edit" button.
   c) Delete Task: Click "Delete" button.
   d) Filter Tasks: Use "All", "Pending", "Completed" buttons.
5. Email Reminders -
   a) Set a due date when creating a task.
   b) System checks every 5 minutes.
   c) Sends email 30 minutes before the due time.
   d) Only sends once per task.

## API Endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
|  POST  |/api/signup|Create new user|
|  POST  |/api/login |Authenticate user|
|  POST  |/api/logout|End user session|
|  GET   |/api/tasks |Get all user tasks|
|  POST  |/api/tasks |Create new task|
|  PUT   |/api/tasks/<id>|Update task|
| DELETE |/api/tasks/<id>|Delete task|

## Testing the Application:

# Test Scenario 1 - User Registration and Login 
1. Create a new account with email and password
2. Verify you're redirected to dashboard
3. Logout and login again with the same credentials

# Test Scenario 2 - Task CRUD Operations 
1. Create: Add 3-4 tasks with different due dates
2. Read: Verify all tasks appear in the list
3. Update: Edit a task title and description
4. Delete: Remove a task and confirm deletion

# Test Scenario 3 - Task Completion 
1. Create several tasks
2. Mark some as completed (checkbox)
3. Use filter buttons to view pending/completed tasks
4. verify completed tasks show with strikethrough

# Test Scenario 4 - Email Reminders 
1. Create a task with due date 30 minutes from now
2. Wait for scheduler to run (checks every 5 minutes)
3. Check your email or console logs after ~5-10 minutes
4. Verify reminder email was sent
5. Confirm reminder_sent flag prevents duplicate emails

# Test Scenario 5 - Overdue Tasks 
1. Create a task with due date in the past
2. Verify it shows "Overdue!" in red text
3. Complete the task to remove the overdue status

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Task
from scheduler import start_scheduler, schedule_task_reminder
from datetime import datetime, timezone
import os
import logging

# Basic logging so we see scheduler and app logs together
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("app")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/todo_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration (Gmail example)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ingaletilottama26@gmail.com'
app.config['MAIL_PASSWORD'] = 'wadl inmy blhg qbwu'
app.config['MAIL_DEFAULT_SENDER'] = 'ingaletilottama26@gmail.com'

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Authentication APIs


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password=hashed_password, name=name)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({'message': 'Login successful', 'user': {'name': user.name, 'email': user.email}}), 200

    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

# Task APIs


@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(
        Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks]), 200


@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()

    # Parse due_date if provided (client should send ISO format)
    due_date = None
    if data.get('due_date'):
        # datetime.fromisoformat may return naive datetimes; scheduler handles naive as UTC
        due_date = datetime.fromisoformat(data.get('due_date'))

    new_task = Task(
        title=data.get('title'),
        description=data.get('description', ''),
        due_date=due_date,
        user_id=current_user.id
    )

    db.session.add(new_task)
    db.session.commit()

    # Schedule reminder for this task (if it has a due_date)
    try:
        if new_task.due_date:
            # schedule_task_reminder will handle timezone-awareness
            schedule_task_reminder(app, app.config.get(
                'SCHEDULER_INSTANCE'), new_task)
            logger.info(
                f"Scheduled reminder for newly created task id={new_task.id}")
    except Exception as e:
        logger.error(
            f"Error scheduling reminder for new task id={new_task.id}: {e}")

    return jsonify(new_task.to_dict()), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)

    if data.get('due_date'):
        task.due_date = datetime.fromisoformat(data.get('due_date'))
    # if due_date not provided, keep existing due_date

    task.completed = data.get('completed', task.completed)

    db.session.commit()

    # Reschedule reminder: remove existing scheduled job (if any) and add new one if applicable
    job_id = f"reminder_{task.id}"
    scheduler = app.config.get('SCHEDULER_INSTANCE')
    if scheduler:
        try:
            scheduler.remove_job(job_id)
            logger.info(
                f"Removed existing scheduler job {job_id} for task {task.id}")
        except Exception:
            # job may not exist; ignore
            pass

        try:
            if task.due_date and not task.completed and not task.reminder_sent:
                schedule_task_reminder(app, scheduler, task)
                logger.info(f"Rescheduled reminder for task id={task.id}")
        except Exception as e:
            logger.error(
                f"Failed to reschedule reminder for task id={task.id}: {e}")
    else:
        logger.warning(
            "Scheduler instance not found in app config; cannot reschedule task reminder.")

    return jsonify(task.to_dict()), 200


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    # Remove scheduled job if exists
    job_id = f"reminder_{task.id}"
    scheduler = app.config.get('SCHEDULER_INSTANCE')
    if scheduler:
        try:
            scheduler.remove_job(job_id)
            logger.info(
                f"Removed scheduled job {job_id} for deleted task {task.id}")
        except Exception:
            # if job didn't exist, ignore
            pass

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Start the background scheduler and store it so we can add/remove jobs at runtime
        scheduler = start_scheduler(app)
        # keep a reference on app.config so request handlers can access it
        app.config['SCHEDULER_INSTANCE'] = scheduler

    print("="*50)
    print("To-Do App with Email Reminders")
    print("="*50)
    print("Server starting on http://localhost:5000")
    print("Background scheduler: One-time jobs scheduled per task")
    print("Reminder timing: 30 minutes before due time")
    print("="*50)

    app.run(debug=True, port=5000)

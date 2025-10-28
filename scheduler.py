from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
from datetime import datetime, timedelta, timezone
from models import Task, User, db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mail = Mail()


def send_email_reminder(app, task, user):
    """Send email reminder for a task"""
    try:
        with app.app_context():
            msg = Message(
                subject=f'Reminder: {task.title}',
                recipients=[user.email],
                html=f"""
                <html>
                    <body style="font-family: Arial, sans-serif; padding: 20px;">
                        <h2 style="color: #4F46E5;">Task Reminder</h2>
                        <p>Hi {user.name},</p>
                        <p>This is a reminder for your upcoming task:</p>
                        <div style="background-color: #F3F4F6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin: 0 0 10px 0; color: #1F2937;">{task.title}</h3>
                            <p style="margin: 5px 0;"><strong>Description:</strong> {task.description or 'N/A'}</p>
                            <p style="margin: 5px 0;"><strong>Due:</strong> {task.due_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                        </div>
                        <p>Don't forget to complete it on time!</p>
                        <p style="color: #6B7280; font-size: 12px; margin-top: 30px;">
                            This is an automated reminder from your To-Do App.
                        </p>
                    </body>
                </html>
                """
            )
            mail.send(msg)

            # Mark reminder as sent
            task.reminder_sent = True
            db.session.commit()

            logger.info(
                f"Email reminder sent to {user.email} for task '{task.title}'")

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        # Log email content to console if sending fails
        logger.info(f"""
        ========== EMAIL REMINDER (Simulated) ==========
        To: {user.email}
        Subject: Reminder: {task.title}
        
        Hi {user.name},
        
        This is a reminder for your upcoming task:
        
        Task: {task.title}
        Description: {task.description or 'N/A'}
        Due: {task.due_date.strftime('%B %d, %Y at %I:%M %p')}
        
        Don't forget to complete it on time!
        ================================================
        """)


def check_and_send_reminders(app):
    with app.app_context():
        try:
            # Calculate the time window (30 minutes from now)
            now = datetime.now(timezone.utc)
            reminder_time = now + timedelta(minutes=30)

            # Find tasks that need reminders
            tasks_needing_reminders = Task.query.filter(
                Task.due_date <= reminder_time,
                Task.due_date > now,
                Task.reminder_sent == False,
                Task.completed == False
            ).all()

            logger.info(
                f"Checking reminders... Found {len(tasks_needing_reminders)} tasks")

            for task in tasks_needing_reminders:
                user = User.query.get(task.user_id)
                if user:
                    send_email_reminder(app, task, user)

        except Exception as e:
            logger.error(f"Error in reminder check: {str(e)}")


def start_scheduler(app):
    """Initialize and start the background scheduler"""
    mail.init_app(app)

    scheduler = BackgroundScheduler()

    # Run the reminder check every 5 minutes
    scheduler.add_job(
        func=lambda: check_and_send_reminders(app),
        trigger='interval',
        minutes=5,
        id='reminder_job',
        name='Check and send email reminders',
        replace_existing=True
    )

    scheduler.start()
    logger.info(
        "Background scheduler started - checking for reminders every 5 minutes")

    return scheduler

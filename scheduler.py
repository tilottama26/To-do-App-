from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
from models import Task, User, db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("scheduler")

mail = Mail()


# ============================================================
# 📨 Function to send the actual email reminder
# ============================================================
def send_email_reminder(app, task, user):
    """Send an email reminder for a task 30 minutes before its due time."""
    try:
        with app.app_context():
            msg = Message(
                subject=f"Reminder: {task.title}",
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
                            <p style="margin: 5px 0;"><strong>Due:</strong> {task.due_date.strftime('%B %d, %Y at %I:%M %p')} IST</p>
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

            # Mark reminder as sent to avoid duplicates
            task.reminder_sent = True
            db.session.commit()

            logger.info(
                f"✅ Email reminder sent to {user.email} for task '{task.title}'")

    except Exception as e:
        logger.exception(
            f"❌ Failed to send email for task '{task.title}': {e}")

        # Mark as sent anyway to avoid retry loops
        task.reminder_sent = True
        db.session.commit()


# ============================================================
# ⏰ Schedule a specific reminder job
# ============================================================
def schedule_task_reminder(app, scheduler, task):
    """Schedule a reminder email to be sent exactly 30 minutes before task due time."""
    now = datetime.now()  # Local IST time
    if not task.due_date:
        logger.warning(
            f"⚠️ Task '{task.title}' has no due date, skipping scheduling.")
        return

    reminder_time = task.due_date - timedelta(minutes=30)

    if reminder_time <= now:
        logger.info(
            f"⏩ Skipping reminder for '{task.title}' — reminder time already passed.")
        return

    user = User.query.get(task.user_id)
    if not user:
        logger.warning(
            f"⚠️ No user found for task ID {task.id}, skipping reminder.")
        return

    scheduler.add_job(
        func=lambda: send_email_reminder(app, task, user),
        trigger="date",
        run_date=reminder_time,
        id=f"reminder_{task.id}",
        replace_existing=True
    )

    logger.info(
        f"🕒 Scheduled reminder for task '{task.title}' at {reminder_time.strftime('%Y-%m-%d %H:%M:%S')} IST")


# ============================================================
# 🚀 Start the scheduler and load all reminders
# ============================================================
def start_scheduler(app):
    """Initialize and start the background scheduler for email reminders."""
    mail.init_app(app)
    scheduler = BackgroundScheduler()
    scheduler.start()

    with app.app_context():
        tasks = Task.query.filter_by(
            reminder_sent=False, completed=False).all()
        logger.info(
            f"📋 Found {len(tasks)} pending tasks to schedule reminders for")

        for task in tasks:
            schedule_task_reminder(app, scheduler, task)

    logger.info("=" * 60)
    logger.info("🚀 Scheduler started")
    logger.info(
        "📬 Email reminders will be sent exactly 30 minutes before due time")
    logger.info("🕒 All times are in IST (no timezone conversion)")
    logger.info("=" * 60)

    return scheduler

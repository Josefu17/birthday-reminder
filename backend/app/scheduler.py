from datetime import datetime, date, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app import database, models, email_service, crud
from app.logger import logger

scheduler = AsyncIOScheduler()


def check_birthdays_job():
    """
        Runs every hour.
        1. Get current hour.
        2. Find rules configured for this hour.
        3. For each rule, calculate the target birthday date.
        4. Find friends with that birthday.
        5. Send emails.
        """
    logger.debug("Checking birthdays...")
    db = database.SessionLocal()

    try:
        current_hour = datetime.now().hour
        today = date.today()

        rules = db.query(models.NotificationRule).filter(
            models.NotificationRule.hour == current_hour
        ).all()

        if not rules:
            logger.debug(f"Hour {current_hour}: No rules scheduled.")
            return

        logger.info(f"Hour {current_hour}: Processing {len(rules)} rules...")

        for rule in rules:
            target_date = today + timedelta(days=rule.days_before)

            friends = crud.get_friends_with_birthday_on_day(db, target_date.month, target_date.day)

            for friend in friends:
                logger.info(f"   -> Sending reminder for {friend.full_name}")
                email_service.send_birthday_email(friend.full_name, rule.days_before)

    except Exception as e:
        logger.error(f"Scheduler Error: {e}", exc_info=True)
    finally:
        db.close()


def start_scheduler():
    # --- PROD MODE (Once per hour) ---
    # scheduler.add_job(check_birthdays_job, 'cron', minute=0)

    # This runs the job every 30 seconds so you can see if it works immediately.
    scheduler.add_job(check_birthdays_job, 'interval', seconds=5)
    scheduler.start()
    logger.info("Scheduler started...")

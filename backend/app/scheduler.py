from datetime import datetime, date, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app import database, email_service, crud
from app.logger import logger

scheduler = AsyncIOScheduler()


def check_birthdays_job():
    logger.info("Running birthdays check...")

    with database.SessionLocal() as db:
        try:
            current_hour = datetime.now().hour
            today = date.today()

            rules = crud.get_rules_by_hour(db, current_hour)

            if not rules:
                logger.debug(f"Hour {current_hour}: No rules scheduled.")
                return

            logger.info(f"Hour {current_hour}: Processing {len(rules)} rule(s)...")

            for rule in rules:
                logger.info(f"Processing rule: {rule}")
                target_date = today + timedelta(days=rule.days_before)

                friends = crud.get_friends_with_birthday_on_day(db, target_date.month, target_date.day)
                if friends:
                    logger.info(f"Found {len(friends)} friend(s) for {target_date.strftime('%d.%m')}")

                for friend in friends:
                    logger.info(f"   -> Sending reminder for {friend.full_name}")
                    email_service.send_birthday_email(friend.full_name, rule.days_before)
        except Exception as e:
            logger.error(f"Scheduler Error: {e}", exc_info=True)


def start_scheduler():
    # --- PROD MODE (Once per hour) ---
    # TODO toggle this in at the end of the project, yb
    # scheduler.add_job(check_birthdays_job, 'cron', minute=0)

    # This runs the job every 30 seconds so you can see if it works immediately.
    scheduler.add_job(check_birthdays_job, 'interval', seconds=10)
    scheduler.start()
    logger.info("Scheduler started...")

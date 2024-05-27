from crontab import CronTab
import os
from sys import argv
from time import time

from src.utils.db_utilities import connect
from src.utils.send_email import send_email
from dotenv import load_dotenv
from os import environ
import logging

logging.basicConfig(filename=os.path.abspath(f'/dev/shm/cron.log'))
logger = logging.getLogger('CRON')
logger.setLevel(logging.DEBUG)

file_time = int(time())

def setup_cron():
    cron = CronTab(user=True)
    venv_path = os.path.abspath(f'{os.getcwd()}/.venv/bin/python3')
    task_path = os.path.abspath(f'{os.getcwd()}/tasks.py')
    job = cron.new(f"{venv_path} {task_path}")
    # run this at the top of every minute
    job.setall("* * * * *")
    cron.write()

def send_emails():
    group_email = environ.get('SMTP_SEND_AS')
    with connect() as conn:
        emails = conn.get_queued_emails()
        for email in emails:
            subject = email[0]['email_subject']
            body = email[0]['email_body']
            to = email[1]
            cc = email[2]
            bcc = email[3]
            try:
                send_email(subject, body, group_email, to, cc, bcc)
                conn.mark_email_as_sent(email[0]['seq'])
            except Exception as e:
                logger.error(e)
                conn.mark_email_as_failed(email[0]['seq'])
                raise e

def maint_db():
    with connect() as conn:
        conn.clear_exp_password_reset()
        conn.reset_failed_emails()


jobs = [maint_db, send_emails]


def main():
    logger.info(f'Running at {file_time=}')
    for func in jobs:
        logger.info(f'Running {func.__name__}')
        try:
            func()
        except Exception as e:
            logger.error(f'Job {func.__name__} failed to run!\n{e}')
            raise e
        else:
            logger.info(f'Job {func.__name__} finished successfully')

if __name__ == "__main__":
    load_dotenv()
    if len(argv) > 1 and argv[1] == '--setup':
        setup_cron()
        exit()

main()
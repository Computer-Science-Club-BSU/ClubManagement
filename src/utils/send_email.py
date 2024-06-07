import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import bs4
from os import environ
from src.utils.cfg_utils import get_smtp_conf

def send_email(subject, body, send_from, to: list, cc: list, bcc: list):
    cnf = get_smtp_conf()
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = send_from
    to_str = ','.join(x['email_id'] for x in to)
    cc_str = ','.join(x['email_id'] for x in cc)
    bcc_str = ','.join(x['email_id'] for x in bcc)
    message['To'] = to_str
    message['Cc'] = cc_str
    message['Bcc'] = bcc_str
    text = bs4.BeautifulSoup(body, "html.parser").text
    message.attach(MIMEText(text, 'plain'))
    message.attach(MIMEText(body, 'html'))
    
    with smtplib.SMTP_SSL(cnf.get("HOST"),
                      cnf.get("PORT")) as server:
        server.login(cnf.get("USER"),
                     cnf.get("PASS"))
        server.sendmail(send_from, to_str, message.as_string())
    return True
    
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import bs4
from os import environ

def send_email(subject, body, send_from, to: list, cc: list, bcc: list):
    
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
    
    with smtplib.SMTP_SSL(environ.get('SMTP_HOST'),
                      int(environ.get('SMTP_PORT'))) as server:
        server.login(environ.get('SMTP_USER'),
                     environ.get('SMTP_PASS'))
        server.sendmail(send_from, to_str, message.as_string())
    return True
    
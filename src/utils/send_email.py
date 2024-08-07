import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import bs4
from os import environ
from src.utils.cfg_utils import get_cfg

def send_email(subject, body, send_from, to: list, cc: list = [], bcc: list = []):
    cnf = get_cfg()['SMTP']
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = send_from
    to_str = ','.join(to)
    cc_str = ','.join(cc)
    bcc_str = ','.join(bcc)
    message['To'] = to_str
    message['Cc'] = cc_str
    message['Bcc'] = bcc_str
    text = bs4.BeautifulSoup(body, "html.parser").text
    message.attach(MIMEText(text, 'plain'))
    message.attach(MIMEText(body, 'html'))
    if send_from == '':
        send_from_email = cnf.get('SEND_AS')
        send_alias = cnf.get('SEND_ALIAS')
        send_from = f"{send_alias} <{send_from_email}>"

    with smtplib.SMTP_SSL(cnf.get("HOST"),
                      cnf.get("PORT")) as server:
        server.login(cnf.get("USER"),
                     cnf.get("PASS"))
        server.sendmail(send_from, to_str, message.as_string())
    return True
    
from src.utils.send_email import send_email
from flask import render_template
from datetime import datetime, timedelta
from base64 import b64encode
from src.utils.cfg_utils import load_config


def send_password_reset(token, recp_email):
    current_time = datetime.now()
    exp_dttm = current_time + timedelta(days=1)
    cfg = load_config()
    reset_address = cfg['public']['sys_addr']
    reset_link = reset_address + '/forgot_password/' + token
    exp_date = exp_dttm.strftime("%m/%d/%Y")
    exp_time = exp_dttm.strftime("%H:%M:%S")
    with open('src/interface/static/logo.png', 'rb') as f:
        logo_data = b64encode(f.read()).decode('utf-8')
    email_body = render_template('email_templates/reset_password_request.liquid',
                                 imgData=logo_data,
                                 resetLink=reset_link,
                                 recp=recp_email,
                                 expDate=exp_date,
                                 expTime=exp_time)


    send_email("Password Reset Requested",
               body=email_body,
               send_from="",
               to=[recp_email],
               cc=[],
               bcc=[])



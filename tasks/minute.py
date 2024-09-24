import os
import subprocess
from src.utils.db_utilities import connect
from src.utils.send_email import send_email
from src.utils.template_utils import load_config
from conf import CFG_DIR

def send_request_emails():
    with connect() as conn:
        requests = conn.fetch_pending_user_requests()
        admin_emails = conn.get_user_admin_emails()
        cfg = load_config()
        for request in requests:
            res = send_email("New user request",
                       f"""A new user request has been submitted.<br>
                       User name: {request['user_name']}<br>
                       First name: {request['first_name']}<br>
                       Last name: {request['last_name']}<br>
                       Email name: {request['email']}<br>
                       This request can be maintained by following these steps:
                       <br>
                       Maintain Users -> Administrate User -> Manage Pending User Requests.
                       """, '', admin_emails, [], [])
            if res:
                conn.update_pending_user_flag(request['seq'], 'A')
            else:
                conn.update_pending_user_flag(request['seq'], 'E')
                raise res[1]

def check_app_reload():
    try:
        open(f'{CFG_DIR}reload', 'r')
        reload_app()
    except FileNotFoundError:
        return

def reload_app():
    os.remove(f'{CFG_DIR}reload')
    subprocess.Popen(['git', 'checkout', '.']).communicate() # Clear our working tree
    subprocess.Popen(['git', 'pull']).communicate() # Pull the new code
    instance = open('/etc/cms/instance').read().strip()
    subprocess.Popen(['sudo', 'systemctl', 'restart', instance]).communicate()

def run_minute():
    send_request_emails()
    check_app_reload()

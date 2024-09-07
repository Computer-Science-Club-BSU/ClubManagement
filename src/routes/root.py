"""Handles all basic "shared" endpoints for the system

Contains the Root '/' path, as well as the before-request handler
"""
import logging
from flask import request, session, send_file
from app import app
from conf import LOG_DIR
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect
from src.utils.permission_checker import check_perms

logger = logging.getLogger("RouteHandler")

@app.route('/', methods=['GET'])
def get_root_index():
    """Serves the / path. Checks if user is signed in.
    If so, customizes their home page and serves the file off to them to be rendered"""
    if 'user_seq' in session:
        # If the user is authenticated in the system, we want to return their
        # "Personalized" page.
        with connect() as conn:
            total = conn.get_finances_total()
            fin_sum = conn.get_finance_summary()
            doc_sum = conn.get_docket_summary()
            is_pos = True
            if total < 0:
                is_pos = False
                total = abs(total)
            gen_log = ""
            access_log = ""
            with open(f'{LOG_DIR}access.log', 'r', encoding='utf-8') as log:
                access_log = [x.strip() for x in log.readlines()]
            with open(f'{LOG_DIR}gen.log', 'r', encoding='utf-8') as log:
                gen_log = [x.strip() for x in log.readlines()]
            home_page_prefs = conn.get_home_widgets(session['user_seq'])

        return render_template('index.liquid', total=total,
                               fin_sum=fin_sum, doc_sum=doc_sum, isPos=is_pos,
                               doc_count=sum(doc_sum.values()),
                               fin_count=sum(fin_sum.values()),
                               gen_log_data=gen_log[-100:],
                               access_log_data=access_log[-100:],
                               top_left = home_page_prefs.get('top_left'),
                               top_right = home_page_prefs.get('top_right'),
                               bot_left = home_page_prefs.get('bot_left'),
                               bot_right = home_page_prefs.get('bot_right')
                               )

    return render_template('index.liquid')

@app.get('/favicon.ico')
def get_favicon_ico():
    return send_file('src/interface/private/favicon.ico')

@app.get('/robots.txt')
def get_robots_txt():
    return send_file('src/interface/private/robots.txt')

@app.before_request
def handle_pre_request():
    """Executes auth checking on all requests and enforces rate limiting on all
    POST requests."""
    # Implement Rate Limiting on POST Requests
    debug_str = ""
    if session.get('user_seq') is not None:
        debug_str += f"User {session.get('user_seq')} "
    else:
        debug_str += "Guest "
    debug_str += f"has issued a {request.method.upper()} request from IP "
    debug_str += f"{request.remote_addr} for resource {request.path}"
    logger.debug(debug_str)
    if request.endpoint in ('static', 'get_favicon_ico', 'get_robots_txt'):
        return

    check_perms(request, session.get('user_seq'), logger)


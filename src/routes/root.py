"""Handles all basic "shared" endpoints for the system

Contains the Root '/' path, as well as the before-request handler
"""
import logging
from flask import request, session
from app import app
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
            with open('/var/log/cms/access.log', 'r', encoding='utf-8') as log:
                access_log = [x.strip() for x in log.readlines()]
            with open('/var/log/cms/gen.log', 'r', encoding='utf-8') as log:
                gen_log = [x.strip() for x in log.readlines()]
            home_page_prefs = conn.get_home_widgets(session['user_seq'])

        return render_template('index.liquid', total=total,
                               fin_sum=fin_sum, doc_sum=doc_sum, isPos=is_pos,
                               doc_count=sum(doc_sum.values()),
                               fin_count=sum(fin_sum.values()),
                               gen_log_data=gen_log[::-1],
                               access_log_data=access_log[::-1],
                               top_left = home_page_prefs.get('top_left'),
                               top_right = home_page_prefs.get('top_right'),
                               bot_left = home_page_prefs.get('bot_left'),
                               bot_right = home_page_prefs.get('bot_right')
                               )

    return render_template('index.liquid')

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

    check_perms(request, session.get('user_seq'), logger)
    # for rule in app.url_map.iter_rules():
    #     if not (rule.rule == request.path):
    #         continue
    #     print(rule.rule, request.path, [
    #         not plugin.check_endpoint_active(rule.endpoint)
    #         for plugin in plugins.values()
    #     ])
    #     print(plugins)
    #     if any([
    #         not plugin.check_endpoint_active(rule.endpoint)
    #         for plugin in plugins.values()
    #     ]):
    #         abort(503)

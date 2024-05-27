from app import app
from src.utils.template_utils import render_template
from flask import request, session, Response, redirect
from src.utils.db_utilities import connect
import logging
from src.utils.permission_checker import check_perms

logger = logging.getLogger("RouteHandler")

@app.route('/', methods=['GET'])
def get_root_index():
    if 'user_seq' in session:
        # If the user is authenticated in the system, we want to return their
        # "Personalized" page.
        with connect() as conn:
            total = conn.get_finances_total()
            fin_sum = conn.get_finance_summary()
            doc_sum = conn.get_docket_summary()
            isPos = True
            if total < 0:
                isPos = False
                total = abs(total)
            gen_log = ""
            access_log = ""
            with open('logs/access.log') as log:
                access_log = [x.strip() for x in log.readlines()]
            with open('logs/gen.log') as log:
                gen_log = [x.strip() for x in log.readlines()]
        return render_template('index.liquid', total=total,
                               fin_sum=fin_sum, doc_sum=doc_sum, isPos=isPos,
                               doc_count=sum(doc_sum.values()),
                               fin_count=sum(fin_sum.values()),
                               gen_log_data=gen_log, access_log_data=access_log
                               )
    
    
    return render_template('index.liquid')


@app.route('/test/')
def get_test():
    return render_template('test/test.liquid')

@app.before_request
def handle_pre_request():
    # Implement Rate Limiting on POST Requests
    debug_str = ""
    if session.get('user_seq') is not None:
        debug_str += f"User {session.get('user_seq')} "
    else:
        debug_str += "Guest "
    debug_str += f"has issued a {request.method.upper()} request from IP "
    debug_str += f"{request.remote_addr} for resource {request.path}"
    logger.debug(debug_str)
    # check_perms(request, session.get('user_seq'), logger)

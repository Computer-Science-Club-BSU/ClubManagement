from app import app
from src.utils.template_utils import render_template
from flask import request, session, Response, redirect
from src.utils.db_utilities import connect
import logging

logger = logging.getLogger("RouteHandler")

@app.route('/', methods=['GET'])
def get_root_index():
    return render_template('index.liquid')


@app.route('/login')
def login():
    session['user_seq'] = 1
    return redirect('/')

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

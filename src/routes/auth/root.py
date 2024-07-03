"""Serves paths relating to Authorization with the server."""
import logging
from flask import request, session, redirect, Response
from app import app
from src.utils.template_utils import render_template
from src.utils.db_utilities import connect


handler = logging.FileHandler('/var/log/cms/access.log')
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

logger = logging.getLogger("AuthManager")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


@app.route("/auth/login/", methods=['GET'])
def get_auth_login():
    """Handles requests to login. Sends login form to user."""
    return Response(render_template("auth/login.liquid"), mimetype='text/html')


@app.route("/auth/login/", methods=['POST'])
def post_auth_login():
    """Serves endpoint for /auth/login/ POST requests. Gets
    data from form, and confirms with database. If invalid, alerts user.
    Logs to log/access.log file"""
    with connect() as conn:
        username = request.form.get('uname')
        logger.info("New Login request for username: %s", username)
        password = request.form.get('pword')
        seq = conn.authorize_user(username, password)
        if seq == -1:
            logger.warning("Login Attempt Failed")
            return Response(render_template("auth/login.liquid",
                                    err="Invalid username or password"),
                                    mimetype='text/html'), 401
        session['user_seq'] = seq
        logger.info("%s Logged in successfully", username)

        return redirect('/')

@app.route("/auth/logout/")
def auth_logout():
    """Handles requests to log out of system.
    Clears session and sends back to home page."""
    session.clear()
    return redirect('/')
